# 패키지와 명령

`post-directory`는 글별 폴더다. 본문과 이미지를 그 폴더 안에 둔다. 근거 경로는 이 폴더 기준이며 로컬 검수에만 쓰인다.

```json
{
  "id": "stable-post-id",
  "title": "독자의 질문이 드러나는 제목",
  "category": "알고리즘/이론",
  "tags": ["다익스트라", "파이썬"],
  "reader_question": "이 글이 답하는 질문",
  "contribution": "기존 글과 비교해 추가되거나 개선된 내용",
  "intent": "new",
  "target_url": null,
  "source_note": "notes.md",
  "sources": [{"kind": "public", "url": "https://example.org/paper", "supports": "어떤 주장에 대한 근거인지"}],
  "experiments": [{"path": "experiment.json", "sha256": "결과 파일의 실제 해시", "supports": "확인한 주장"}],
  "images": [{"path": "img/graph.png", "purpose": "반례의 간선 방향과 가중치를 보여준다"}],
  "review": {"technical": false, "visual": false, "notes": ""}
}
```

`intent`는 `new` 또는 `update`. 업데이트는 대상 블로그의 실제 `target_url`을 사용한다. `review`는 실제 검토 후만 변경한다. 기계 검사는 검토 플래그를 자동으로 올리지 않는다.

로컬 실험 코드를 함께 보관한다면 `experiments` 항목에 `script` 경로와 `script_sha256`도 넣는다. 결과 파일뿐 아니라 실행 코드가 바뀌었을 때도 재검증이 필요함을 잡아준다.

## 명령

```bash
python3 scripts/blog.py catalog --config blog-workflow/config.json
python3 scripts/blog.py lint-notes notes.md
python3 scripts/blog.py check post-directory
python3 scripts/blog.py preview post-directory
python3 scripts/blog.py record-publication post-directory --config blog-workflow/config.json --status draft --url ACTUAL_EDITOR_URL --observation '저장 목록과 재열기에서 제목·본문·이미지를 확인함'
python3 scripts/blog.py verify-public post-directory --config blog-workflow/config.json --url ACTUAL_PUBLIC_URL
```

`record-publication --status published`는 `verify-public`이 최신 본문 해시에 대해 통과하고, 해당 실제 URL과 일치할 때만 기록된다. 이미지·단락의 시각 검수는 자동 검사의 한계 밖이므로 브라우저 관측도 남긴다. URL, 상태, 내용 해시, 확인 시각은 별도로 저장된다. 이전 버전의 확인 기록을 현재 버전에 재사용하지 않는다.

`verify-public`은 HTTP 200만으로 성공 처리하지 않는다. 게시글 본문 컨테이너, 제목, 대표 문장, 이미지·코드·표 수, 내부 링크 상태를 확인한다. 이미지 개수만으로 업로드 내용·위치의 동일성이 증명되지는 않는다.
