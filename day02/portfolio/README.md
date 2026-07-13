# I AM — 포트폴리오 (2일차 · MPA + Tailwind + Apple Design)

## 폴더 구조
```
site/
├── index.html        # 홈 (히어로 · 핵심역량 · 기술스택 · CTA)
├── projects.html     # 프로젝트 3종 + 상세 모달
├── about.html        # 타임라인 · 학습 · Travel Log · Sound
├── playground.html   # 반응속도 게임 + 방명록
├── common.js         # 공통 스크립트 전부 + 한/영 사전
└── assets/
    ├── style.css     # reveal/타임라인/토스트 등 커스텀 CSS
    └── *.png/jpg     # 데이터아트 + 여행 사진
```
네비게이션·푸터는 네 페이지에 **바이트 단위로 동일**하게 삽입돼 있습니다(명세 2-2).

## 로컬 실행
VS Code에서 `site/` 폴더 열기 → `index.html` 우클릭 → **Open with Live Server**.
(더블클릭 file:// 로도 동작하지만, Live Server 권장)

## 구현 기능
| 구분 | 기능 | 위치 |
|---|---|---|
| 필수 | MPA 4페이지 + 현재 페이지 표시(aria-current) + 햄버거 | 공통 |
| 필수 | Tailwind CDN + 커스텀 config(다크모드 class 전략, 색 토큰) | `<head>` |
| 도전 | 다크모드 토글 (localStorage 저장, OS 설정 감지) | 네비 ☾ 버튼 |
| 도전 | 스크롤 진행률 바 | 최상단 2px 블루 바 |
| 도전 | 프로젝트 상세 모달 (Esc/배경클릭/포커스 복원) | projects |
| 도전 | 인터랙티브 타임라인 (스크롤 따라 라인·점 채움) | about |
| 도전 | 한/영 토글 (data-i18n 사전 방식, localStorage 저장) | 네비 EN 버튼 |
| 도전 | 방명록 (localStorage, 30개 캡, 삭제 가능) | playground |
| 도전 | 반응속도 테스트 게임 (최고기록 localStorage 저장) | playground |
| 도전 | 제너레이티브 로파이 플레이어 (Web Audio API + 비주얼라이저) | about Sound |
| 도전 | 여행 블로그 미리보기 (인터마이애미 사진 + 카드 3장) | about Travel Log |
| 도전 | 이스터에그 ×3 | 아래 스포일러 |

## 수정 포인트
- **여행 카드**: `build_pages.py`의 Travel Log 섹션에서 카드 제목/문구/링크 수정. 문구는 `common.js`의 `tv1.p`~`tv3.p` 키(한/영 둘 다). 링크는 네이버 블로그(`blog.naver.com/lsj020111`), 썸네일은 `assets/travel_miami.jpg`.
- **반응속도 게임**: `common.js`의 `initGame()`. 등급 컷(220/300/400ms)과 문구는 `game.rank.*` 키로 조정.
- **방명록**: localStorage 데모라 방문자 각자의 브라우저에만 저장됩니다. 진짜 공유 방명록은 Netlify Forms로 교체 가능.
- **음악**: 저작권 문제로 실제 음원 대신 브라우저가 실시간 생성하는 로파이 루프입니다. 진짜 곡은 Spotify embed(iframe)로 교체 가능.
- **문구/번역**: 모든 텍스트는 `common.js` 상단 `I18N` 사전에서 관리. **ko/en 양쪽에 같은 키**가 있어야 합니다.
- **페이지 생성 방식**: HTML을 직접 손으로 고치지 말고 `build_pages.py`를 수정한 뒤 `python3 build_pages.py`로 다시 찍어내면, 네비/푸터가 4페이지에 자동으로 동일하게 반영됩니다.

## Git 커밋 플랜 (명세 2-1)
```bash
git init
git add . && git commit -m "chore: 1일차 SPA 결과물 초기 커밋"      # 1일차 파일 기준
# MPA 파일로 교체 후
git commit -am "feat: MPA 구조 전환 (3페이지 + 공통 네비게이션)"
git commit -am "style: Tailwind CSS 전환"
git commit -am "feat: 다크모드 토글 + 스크롤 진행률 바"
git commit -am "feat: 프로젝트 상세 모달 + 데이터아트 이미지 복원"
git commit -am "feat: 인터랙티브 타임라인"
git commit -am "feat: 한/영 다국어 토글 (i18n 사전)"
git commit -am "feat: 방명록 (localStorage)"
git commit -am "feat: 제너레이티브 로파이 플레이어 + 여행 로그"
git commit -am "feat: 이스터에그 (히든 배지·SSAFY 코드·콘솔)"
git commit -am "feat: Playground 페이지 추가 (반응속도 게임 + 방명록 이동)"
git commit -am "feat: 기술 스택 칩 호버 인터랙션 + SSAFY 이력 추가"
git commit -am "style: Apple 디자인 시스템 적용 리뉴얼"
```
한 번에 커밋하지 말고, 파일을 기능 순서대로 반영하면서 위 단위로 나눠 커밋하세요.

## Netlify 배포
- 가장 빠른 방법: `site/` 폴더를 Netlify 드롭존에 **드래그 앤 드롭** (index.html이 최상위라 바로 동작).
- 권장: GitHub 저장소 연결 → push 때마다 자동 배포. Build command/Publish directory는 비워두면 됩니다(정적 사이트).

## 이스터에그 (스포일러 ⚠)
1. 로고(SUNJAE LEE) **7연타** → 히든 배지 ★ 영구 획득
2. 아무 화면에서 키보드로 **`ssafy`** 타이핑 → 토스트
3. 개발자도구 **콘솔**을 열면 채용 메시지
