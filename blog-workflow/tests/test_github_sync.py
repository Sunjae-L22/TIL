"""End-to-end Git tests use temporary bare remotes; no GitHub writes."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('github_sync', ROOT/'skills/tistory-post/scripts/github_sync.py')
gs = importlib.util.module_from_spec(spec);spec.loader.exec_module(gs)


def git(root, *args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True,stderr=subprocess.PIPE).strip()


class GitSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.repo=self.base/'work';self.repo.mkdir()
        self.remote=self.base/'remote.git'
        git(self.repo,'init','-b','master');git(self.repo,'config','user.name','TIL test')
        git(self.repo,'config','user.email','til@example.invalid')
        git(self.repo,'config','commit.gpgsign','false')
        git(self.repo,'config','core.hooksPath',str(self.base/'hooks'))
        (self.repo/'old.md').write_text('기존 노트\n');(self.repo/'other.md').write_text('다른 노트\n')
        git(self.repo,'add','old.md','other.md');git(self.repo,'commit','-m','initial')
        git(self.repo,'init','--bare',str(self.remote));git(self.repo,'remote','add','origin',str(self.remote))
        git(self.repo,'push','origin','master')
        self.initial=git(self.repo,'rev-parse','HEAD')
        self.cfg=self.base/'config.json';self.cfg.write_text(json.dumps({'notes_root':'work','git_sync':{'enabled':True,'remote':'origin','branch':'master','expected_url':str(self.remote)}}))

    def new(self):
        (self.repo/'새노트.md').write_text('검증한 노트다.\n\n```python\nprint(1)\n```\n')
        return ['새노트.md']

    def tip(self):return git(self.remote,'rev-parse','refs/heads/master')

    def test_selected_commit_preserves_other_staged_and_untracked_work(self):
        names=self.new();(self.repo/'other.md').write_text('사용자가 스테이지한 내용\n')
        git(self.repo,'add','other.md');staged=git(self.repo,'rev-parse',':other.md')
        (self.repo/'scratch.md').write_text('아직 작성 중\n')
        result=gs.sync(self.cfg,names,'TIL 정리')
        self.assertEqual(result['status'],'synced');self.assertEqual(result['commit'],self.tip())
        self.assertEqual(git(self.repo,'rev-parse',':other.md'),staged)
        self.assertEqual(git(self.repo,'show','HEAD:other.md'),'다른 노트')
        self.assertNotEqual(git(self.repo,'diff','--cached','--name-only'),'')
        self.assertIn('scratch.md',git(self.repo,'ls-files','--others','--exclude-standard'))
        self.assertEqual(git(self.repo,'diff','--name-only','HEAD','--','새노트.md'),'')

    def test_unchanged_note_makes_no_commit(self):
        self.assertEqual(gs.sync(self.cfg,['old.md'],None)['status'],'no_changes')
        self.assertEqual(self.initial,self.tip())

    def test_unrelated_ahead_commit_is_not_pushed(self):
        (self.repo/'other.md').write_text('다른 미발행 작업\n');git(self.repo,'add','other.md');git(self.repo,'commit','-m','other work')
        with self.assertRaises(gs.SyncError):gs.sync(self.cfg,self.new(),'TIL')
        self.assertEqual(self.initial,self.tip())

    def test_remote_destination_mismatch_stops(self):
        cfg=json.loads(self.cfg.read_text());cfg['git_sync']['expected_url']='https://github.com/elsewhere/TIL.git';self.cfg.write_text(json.dumps(cfg))
        with self.assertRaises(gs.SyncError):gs.plan(self.cfg,self.new())
        self.assertEqual(self.initial,git(self.repo,'rev-parse','HEAD'))

    def test_selected_staged_work_is_untouched(self):
        (self.repo/'old.md').write_text('중간 변경\n');git(self.repo,'add','old.md')
        staged=git(self.repo,'rev-parse',':old.md');(self.repo/'old.md').write_text('아직 준비 중\n')
        with self.assertRaises(gs.SyncError):gs.sync(self.cfg,['old.md'],'TIL')
        self.assertEqual(staged,git(self.repo,'rev-parse',':old.md'))

    def test_missing_or_unselected_image_blocks_then_linked_image_is_pushed(self):
        names=self.new();(self.repo/names[0]).write_text('![그림](img/graph.png)\n')
        with self.assertRaises(gs.SyncError):gs.plan(self.cfg,names)
        (self.repo/'img').mkdir();(self.repo/'img/graph.png').write_bytes(b'fixture image')
        with self.assertRaises(gs.SyncError):gs.plan(self.cfg,names)
        result=gs.sync(self.cfg,names+['img/graph.png'],'노트와 그림')
        self.assertEqual(result['commit'],self.tip())

    def test_private_draft_and_symlink_are_rejected(self):
        (self.repo/'blog-workflow').mkdir();(self.repo/'blog-workflow/private.md').write_text('private')
        with self.assertRaises(gs.SyncError):gs.plan(self.cfg,['blog-workflow/private.md'])
        (self.repo/'outside.md').symlink_to(self.cfg)
        with self.assertRaises(gs.SyncError):gs.plan(self.cfg,['outside.md'])

    def test_workspace_instructions_are_not_auto_published_as_notes(self):
        for name in ['AGENTS.md','README.md']:
            (self.repo/name).write_text('Repository instructions\n')
            with self.assertRaises(gs.SyncError):gs.plan(self.cfg,[name])
        self.assertEqual(self.initial,self.tip())

    def test_invalid_markdown_does_not_commit(self):
        names=self.new();(self.repo/names[0]).write_text('```python\nprint(1)\n')
        with self.assertRaises(gs.SyncError):gs.sync(self.cfg,names,'invalid')
        self.assertEqual(self.initial,git(self.repo,'rev-parse','HEAD'))

    def failed_push(self,names):
        real_git=gs.git
        def fail(root,*args,**kwargs):
            if args and args[0]=='push':raise gs.SyncError('simulated network failure')
            return real_git(root,*args,**kwargs)
        with patch.object(gs,'git',side_effect=fail):
            with self.assertRaises(gs.SyncError):gs.sync(self.cfg,names,'TIL')

    def test_failed_push_retries_same_commit(self):
        self.failed_push(self.new());head=git(self.repo,'rev-parse','HEAD')
        result=gs.sync(self.cfg,[],None)
        self.assertEqual(head,result['commit']);self.assertEqual(head,self.tip())
        self.assertEqual(git(self.repo,'rev-list','--count','HEAD'),'2')

    def test_lost_push_response_does_not_duplicate_commit(self):
        real_git=gs.git
        def lose(root,*args,**kwargs):
            result=real_git(root,*args,**kwargs)
            if args and args[0]=='push':raise gs.SyncError('simulated response loss')
            return result
        with patch.object(gs,'git',side_effect=lose):result=gs.sync(self.cfg,self.new(),'TIL')
        self.assertEqual(result['commit'],self.tip())
        self.assertEqual(git(self.repo,'rev-list','--count','HEAD'),'2')

    def test_remote_advance_blocks_pending_retry(self):
        self.failed_push(self.new())
        other=self.base/'other';git(self.repo,'clone',str(self.remote),str(other))
        git(other,'config','user.name','remote test');git(other,'config','user.email','remote@example.invalid');git(other,'config','commit.gpgsign','false')
        (other/'remote.md').write_text('원격 변경\n');git(other,'add','remote.md');git(other,'commit','-m','remote update');git(other,'push','origin','master')
        with self.assertRaises(gs.SyncError):gs.sync(self.cfg,[],None)
        self.assertEqual(self.tip(),git(other,'rev-parse','HEAD'))

    def test_hook_scope_change_cannot_be_pushed_on_retry(self):
        hooks=self.base/'hooks';hooks.mkdir()
        hook=hooks/'pre-commit';hook.write_text('#!/bin/sh\nprintf "hook change\\n" > extra.md\ngit add extra.md\n');hook.chmod(0o755)
        with self.assertRaises(gs.SyncError):gs.sync(self.cfg,self.new(),'TIL')
        with self.assertRaises(gs.SyncError):gs.sync(self.cfg,[],None)
        self.assertEqual(self.initial,self.tip())


if __name__=='__main__':unittest.main()
