# GitHub 튜토리얼

> Github 계정 생성 및 초기 설정 정리

- main -> master로 변경 : git bash에서도 master이기 때문

- Create new Repository (원격 저장소 생성)
  - git에서 commit을 통해 관리한 버전들을 업로드하는 공간
  - README.md : 프로젝트의 소개글
  - TIL Repository : 오늘 배운 걸 올리는 국룰 레포
  - 내가 이미 기록을 남겼던 적이 있다면? -> 원격 저장소는 비어있는 상태로 만들기
  - 아직 아무것도 안했다? -> README, gitignore, license 추가해도 됨(새 폴더에서 touch READMD.md 한다음에 git init한거랑 똑같음)
  - 기존 작업중인 폴더에 원격저장소 추가 : git remote add (별명) (주소)
  - 여러 개의 원격저장소 추가 가능(github, gitlab 등등...) -> git remote -v를 통해 추가한 원격저장소 목록 확인 가능
  - 원격저장소 하나당 fetch, push가 보일텐데 fetch는 변동사항이 있는지 확인, push는 업로드
  - git push (어디에) (누가작업했는지) -> git push origin master
  - **git add** : 각 파일 작업이 끝났을때 사용
  - **git commit** : 작업 한 사이클이 끝났을때 사용
  - **git push** : 집에 가기 전에 원격 저장소에 push
  - git push -u origin master : 첨에 한번만 하면 그담엔 git push만 해도 origin master로 push
