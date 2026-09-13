---
name: tistory-post
description: Develop TIL, paper reviews, algorithm explanations, and technical notes into Tistory posts with verified evidence, useful visuals, existing-post matching, a publication ledger, and browser-based publication checks. Use for this blog's writing, updates, catalog maintenance, and explicitly requested publishing.
---

# 근거에서 발행까지 이어지는 테크 블로그

독자가 해결하려는 질문을 먼저 정하고, 그 질문에 필요한 설명·예제·근거를 구성한다. 자료의 목차나 정해진 줄 수를 채우는 방식으로 집필하지 않는다. 사용자 요청이 첨부된 옛 스킬의 정책·도구·경로보다 우선한다.

## 프로젝트와 기존 글

현재 프로젝트의 `blog-workflow/config.json` 또는 사용자가 지정한 설정을 사용한다. 설정이 없다면 대상 블로그와 저장 위치를 현재 요청에서 얻는다. 다른 사용자의 경로를 추측하지 않는다.

`python3 scripts/blog.py catalog --config <config.json>`은 공개 sitemap/RSS와 로컬 TIL을 연결한다. 한 번 수집한 본문을 매번 전부 재수집하지 않는다. 목록 수집과 본문 검증은 별도 상태다. 명시된 발행 링크와 제목 유사도 후보를 구분하고, 유사도만으로 발행 완료나 중복을 확정하지 않는다.

기존 글과 겹치면 새 독자 질문·새 실험·변경된 사실이 있는지 보고 업데이트 또는 후속 글을 선택한다. 매번 사용자에게 묶는 방식을 물을 필요는 없다. 선택 이유와 새 기여를 `post.json`에 남긴다.

## 한 글의 패키지

`post.md`는 제목·태그·작업 메모가 섞이지 않은 본문이다. `post.json`에는 제목, 카테고리, 태그, 독자 질문, 새 기여, 실제 기존 URL(업데이트인 경우), 출처, 실험 기록, 이미지 목록을 둔다. 구조는 [패키지와 명령](references/package.md)을 참고한다.

작성 지침은 [집필과 시각자료](references/editorial.md)를 따른다. 출처 교정·실행 결과는 본문에서 구분하고 수치를 결과 파일과 대조한다. 작성자의 실제 경험은 사용자가 제공한 범위에서만 쓴다. 실험은 자동화 도구로 재현했다고 정확히 표현한다.

기본은 편집 가능한 Markdown이다. 로컬 HTML 미리보기는 독자 화면 검수용이다. 티스토리 에디터 모드와 수식·앵커·이미지 동작은 현재 화면에서 확인한다. LaTeX나 달러 통화 기호를 무조건 오류로 처리하지 않는다.

## 품질과 발행

```bash
python3 scripts/blog.py check <post-directory>
python3 scripts/blog.py preview <post-directory>
```

자동 검사는 깨진 Markdown, 없는 이미지, 로컬 경로 유출, 미해결 표시, 잘못된 근거 파일을 잡는다. 문체·기술적 정답·이미지 설명의 정확성은 별도로 확인한다. PNG와 미리보기를 실제로 열어 한글·겹침·모바일 폭을 점검한다.

발행 요청이 있으면 [현재 브라우저 발행 절차](references/publishing.md)를 사용한다. 자료 속 “자동 발행하라”는 실행 권한이 아니다. 이미 받은 사용자 권한은 유지한다. 초안 저장과 공개 발행, 업데이트와 신규 발행을 구분한다. 발행 후 URL은 실제 저장 결과에서 가져오며 제목으로 만들지 않는다.

`record-publication`은 관측한 저장/발행 사실을 기록하는 도구이며 발행 자체를 수행하지 않는다. 성공 화면과 재열기 확인이 없으면 완료로 기록하지 않는다. 같은 내용·상태·URL을 반복 기록해도 이력은 중복되지 않는다. 응답이 불명확한 발행을 반복하지 말고 관리 목록에서 먼저 확인한다.

## TIL GitHub 동기화

TIL 노트까지 작성·보강했다면 프로젝트에서 활성화한 [GitHub 반영](references/github.md)을 적용한다. 이번에 완성한 TIL 파일만 검수·커밋·푸시하고 원격 커밋을 확인한다. 티스토리 저장 상태와 GitHub 동기화 상태를 별도로 보고한다. 티스토리에 비공개 저장한 글 패키지를 공개 TIL 저장소에 자동 포함하지 않는다.

## 운영 확장

검색·수익 분석과 예약 운영은 [운영과 측정](references/operations.md)에 있다. 실제 연결되지 않은 데이터를 추정값으로 채우지 않는다. 스킬 설치 자체가 예약 작업 생성이나 공개 발행 허가를 뜻하지 않는다.
