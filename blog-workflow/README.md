# It것저것 블로그 워크플로

자료 판독에서 검증된 원고와 발행 이력까지 이어가는 첫 버전이다. 원본 Claude 스킬을 그대로 실행하지 않고 Codex 환경에 맞춰 재구성했다.

## 현재 사용할 수 있는 것

- **PDF 공부 노트**: 페이지별 추출, 필요한 페이지 렌더링, 실제 판독 여부와 범위 기록, 원본 변경 감지.
- **티스토리 원고**: 독자 질문과 새 기여 기록, 원고/메타데이터 분리, 이미지·근거·Markdown 검수, 독자 화면 미리보기.
- **기존 글 연결**: 공개 글 172개와 TIL 55개의 카탈로그. 명시된 발행 링크와 제목 유사 후보를 구분한다.
- **TIL GitHub 동기화**: 완성한 TIL 파일과 연결된 그림만 검수·커밋·푸시하고 원격 커밋을 확인한다. 현재 대상은 `Sunjae-L22/TIL`의 `master`다. [설정과 재시도](skills/tistory-post/references/github.md)를 참고한다.
- **발행 기록**: 실제 주소·내용 해시·상태 전환을 기록하며, 공개 확인 전에는 발행 완료로 기록하지 않는다.
- **비공개 저장 실증**: 대표 원고를 티스토리에 저장하고 다시 열어 그림·코드·표·태그를 확인했다. [저장된 글 수정](https://it-study-2002.tistory.com/manage/post/175)에서 열 수 있다.
- **대표 검증 패키지**: [원고 미리보기](posts/dijkstra-negative-edge/preview.html), [편집 가능한 본문](posts/dijkstra-negative-edge/post.md), [공부 노트](posts/dijkstra-negative-edge/notes.md), [실험 결과](posts/dijkstra-negative-edge/experiment.json).

두 스킬은 `~/.codex/skills/pdf-study-notes`와 `~/.codex/skills/tistory-post`에서 이 프로젝트의 스킬 폴더를 가리키도록 설치했다. 원본 handoff 폴더는 수정하지 않았다. 이 TIL 폴더를 이동하면 링크도 새 위치로 바꿔야 한다.

## 사용하는 방법

Codex에서 다음처럼 요청하면 된다.

- `$pdf-study-notes 이 PDF를 기존 TIL과 연결해서 정리하고, 출처 페이지와 실제 검증 결과를 남겨줘.`
- `$tistory-post 이 노트를 기존 글과 대조해 새 글 또는 보강안을 만들고, 원고와 이미지를 검수해줘.`
- `$tistory-post 이 패키지를 티스토리에 비공개 저장하고, 다시 열어서 확인한 뒤 이력을 기록해줘.`

TIL 작성·수정 작업이 끝나면 GitHub 반영까지 이어간다. 루트 `AGENTS.md`와 두 스킬에서 이 절차를 호출한다. 초안만 작성하거나 로컬에만 남기라는 현재 요청이 있으면 그 요청을 따른다. 파일 저장 이벤트를 감시하는 백그라운드 작업은 아니다.

공개 발행·기존 글 수정·정기 발행은 요청된 범위를 따른다. 이번 구현에서 예약 작업은 만들지 않았다. `config.json`의 `publication_mode`는 초안이며 예약 주기는 미정이다. 모드 설정만으로 브라우저가 자동 실행되지는 않는다.

## 작업 결과 찾기

| 파일 | 용도 |
|---|---|
| [config.json](config.json) | 블로그·자료·상태 저장 위치와 운영 기본값 |
| [카탈로그](state/catalog.md) | TIL에 적힌 발행 링크와 제목 연결 후보 |
| `state/catalog.json` | 다음 작업이 재사용하는 기계 판독용 목록 |
| [발행 이력](state/publications.json) | 실제 관측한 저장·발행 이력 |
| [브라우저 점검](state/browser-check.json) | 현재 로그인·본문 입력·업로드 검증 상태 |
| [검증 보고서](validation/report.md) | 스킬·도구·대표 원고 검증과 제한 사항 |

## 도구를 직접 실행할 때

Python 3.11 이상, `requirements.txt`의 패키지, Poppler의 `pdfinfo`, `pdftotext`, `pdftoppm`을 사용한다. 현재 기기의 Python 3.11 환경에는 필요한 패키지가 설치되어 있다. 새 환경에서는 프로젝트 가상환경에 의존성을 설치한다. 시스템 Python 패키지를 강제 변경하지 않는다.

TIL 폴더에서 실행한다.

```bash
python3 blog-workflow/skills/tistory-post/scripts/blog.py catalog --config blog-workflow/config.json
python3 blog-workflow/skills/tistory-post/scripts/blog.py check blog-workflow/posts/dijkstra-negative-edge
python3 blog-workflow/skills/tistory-post/scripts/blog.py preview blog-workflow/posts/dijkstra-negative-edge
python3 -m unittest discover -s blog-workflow/tests -v
```

공개 글 카탈로그는 sitemap/RSS 2개를 읽고, 모든 본문을 반복 수집하지 않는다. 실패한 조회는 마지막 정상 목록을 덮어쓰지 않는다. 제목 후보를 확인한 실제 링크로 확정하는 작업은 원고 제작 시 수행한다.

GitHub에는 워크플로 도구·스킬·설정·테스트를 보관한다. 위 목록의 `posts/`, `state/`, `validation/` 파일은 로컬 작업 결과이며 `.gitignore`로 제외해 GitHub 복제본에는 없다. PDF 처리 중간 이미지·추출문과 원본 경로가 있는 판독 상태도 제외했다. 공개용 본문/이미지와 비공개 원본은 구분해 보관한다. 발행할 때 글 폴더 전체를 업로드하지 않는다.

## 다음 연결 지점

1. 실제 Search Console 지표를 연결해 다음 글·보강 글 우선순위를 정한다. 현재 해당 연결은 구성하지 않았다.
2. 주기와 발행 범위가 정해지면 Codex 예약 실행을 연결한다. 로컬 파일 기반 실행은 컴퓨터와 앱이 실행 중이어야 한다.

애드센스 승인 여부와 수익 데이터는 이번 구현의 검증 대상이 아니다. 수익을 추정해 채운 파일은 없다.
