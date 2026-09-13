"""Regression checks for meaningful publication and source-evidence boundaries."""
from pathlib import Path
import argparse
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


blog = module('blog', 'skills/tistory-post/scripts/blog.py')
study = module('study', 'skills/pdf-study-notes/scripts/study.py')


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.post = self.root / 'post'; self.post.mkdir()
        self.meta = {'id':'sample','title':'검증하는 알고리즘','category':'알고리즘',
                     'reader_question':'어떤 조건에서 성립하는가?','contribution':'반례',
                     'tags':['알고리즘'],'intent':'new','sources':[{'kind':'public',
                     'url':'https://example.org/source','supports':'이론'}],
                     'images':[], 'review':{'technical':True,'visual':True}}
        self.body = ('이 설명은 입력 조건과 실행 결과를 함께 확인하며 짧은 사례 하나로 일반적인 결론을 내리지 않는다.\n\n'
                     '서로 다른 구현의 출력은 같은 입력과 독립적인 기준 결과로 비교한 뒤에 본문에 반영한다.\n')
        self.save()
        self.cfg = self.root / 'config.json'
        self.cfg.write_text(json.dumps({'blog_url':'https://test.tistory.com','state_dir':'state','posts_dir':'.','notes_root':'.'}))

    def save(self):
        (self.post/'post.json').write_text(json.dumps(self.meta,ensure_ascii=False))
        (self.post/'post.md').write_text(self.body)

    def args(self, status='draft', url='https://test.tistory.com/manage/post/1'):
        return argparse.Namespace(directory=str(self.post),config=str(self.cfg),status=status,url=url,observation='Fixture saved and reopened')

    def test_real_markdown_code_containers(self):
        for text in ['```python\nprint(1)\n```\n','> ```python\n> print(1)\n> ```\n','    print(1)\n']:
            self.assertFalse(blog.lint(text)['errors'])
        self.assertTrue(blog.lint('```python\nprint(1)\n')['errors'])

    def test_currency_is_not_latex(self):
        self.assertFalse(blog.lint('요금은 $5다.',post=True)['errors'])

    def test_tistory_numeric_tildes_warn_only_in_prose(self):
        self.assertTrue(blog.lint('정점 4~10개, 가중치 -6~9.',post=True)['warnings'])
        self.assertFalse(blog.lint('정점 4개부터 10개까지.',post=True)['warnings'])
        self.assertFalse(blog.lint('```python\n# 4~10\n```\n',post=True)['warnings'])

    def test_table_with_extra_cell_fails(self):
        self.assertTrue(blog.lint('|a|b|\n|---|---|\n|1|2|3|')['errors'])

    def test_raw_html_cannot_bypass_asset_checks(self):
        for raw in ['<img src="missing.png">','<a href="notes.md">로컬 파일</a>']:
            self.assertTrue(blog.lint(raw,post=True)['errors'])

    def test_concrete_sources_required(self):
        for sources in [[{}],[{'kind':'public','url':'file:///private/source','supports':'claim'}]]:
            self.meta['sources']=sources;self.save()
            self.assertFalse(blog.check_post(self.post)['ok'])

    def test_changed_experiment_fails(self):
        file=self.post/'experiment.json';file.write_text('{"answer":1}')
        self.meta['experiments']=[{'path':file.name,'sha256':blog.sha(file),'supports':'answer'}];self.save()
        self.assertTrue(blog.check_post(self.post)['ok'])
        file.write_text('{"answer":2}')
        self.assertFalse(blog.check_post(self.post)['ok'])

    def test_ledger_retry_and_real_transition(self):
        a=self.args();blog.record_publication(a)
        self.assertTrue(blog.record_publication(a)['already_recorded'])
        blog.record_publication(self.args('publication_unknown'))
        self.assertFalse(blog.record_publication(a).get('already_recorded',False))
        events=json.loads((self.root/'state/publications.json').read_text())
        self.assertEqual([e['status'] for e in events],['draft','publication_unknown','draft'])

    def test_wrong_update_target_fails_before_fetch(self):
        self.meta.update(intent='update',target_url='https://test.tistory.com/1');self.save()
        with patch.object(blog,'fetch') as fetch:
            with self.assertRaises(ValueError):blog.verify_public(self.args(url='https://test.tistory.com/2'))
            fetch.assert_not_called()

    def test_current_verification_required(self):
        url='https://test.tistory.com/1'
        with self.assertRaises(FileNotFoundError):blog.record_publication(self.args('published',url))
        blog.write(self.post/'public-verification.json',{'ok':True,'url':url,'content_sha256':blog.content_hash(self.post)})
        blog.record_publication(self.args('published',url))
        self.body+='\n새로 바꾼 문장이다.\n';self.save()
        with self.assertRaises(ValueError):blog.record_publication(self.args('published',url))

    def test_http200_without_article_fails(self):
        a=self.args(url='https://test.tistory.com/1')
        with patch.object(blog,'fetch',return_value=(b'<html>Sign in</html>',a.url)):
            self.assertFalse(blog.verify_public(a)['ok'])

    def test_indented_code_public_verification(self):
        self.body+='\n    print(1)\n';self.save();a=self.args(url='https://test.tistory.com/1')
        page='<meta property="og:title" content="'+self.meta['title']+'"><div class="contents_style">'+blog.MD.render(self.body)+'</div>'
        with patch.object(blog,'fetch',return_value=(page.encode(),a.url)):
            self.assertTrue(blog.verify_public(a)['ok'])

    def test_partial_reading_is_not_whole_source(self):
        src=self.root/'source.pdf';src.write_bytes(b'fixture source')
        work=self.root/'study';work.mkdir();text=work/'page.txt';text.write_text('source')
        manifest={'source':{'path':str(src),'sha256':study.digest(src),'pages':3},'selected_pages':[1],
                  'pages':{'1':{'status':'extracted','text_path':'page.txt','text_sha256':study.digest(text)}}}
        study.write(work/'manifest.json',manifest);a=argparse.Namespace(workdir=str(work))
        self.assertFalse(study.check(a)['ok'])
        manifest['pages']['1']['status']='covered';study.write(work/'manifest.json',manifest)
        report=study.check(a);self.assertTrue(report['ok']);self.assertFalse(report['whole_source_covered'])
        text.write_text('changed');self.assertFalse(study.check(a)['ok'])


if __name__=='__main__':unittest.main()
