# GIT이란?


## 분산 버전 관리 시스템
- 버전 관리 : 변화를 기록하고 추적하는 것(3.11.7 -> 메이저(대격변), 마이너(새롭게 추가되거나 보안된 무언가), 패치)
- 분산 : 버전을 여러 개의 복제된 저장소에 저장 및 관리


## Git의 3가지 영역 -> Github, Gitlab 이런거랑 다른거임
- Working Directory : 실제 작업 중인 파일들이 위치한 영역
- Staging Area : 준비단계(다음 버전에 포함시킬 파일들만 선택적으로 추가하는 단계 : git add)
- Repository : commit(버전을 만드는 행위)을 통해 Repository에 옮겨담는다

## Git으로 관리하기
- git init : initialize -> (master)라는 곳에서 관리하고 있다고 확인 가능
- git status : 상태 확인 가능 -> untracked files : 아직 버전이 없어서 git은 모름!
- git add (경로) : staging area에 (무언가)를 추가해줘 -> git status 시 changes to be commited가 생긴다
- git rm --cashed : 를 통해 언스테이징 가능
- git commit : 버전 생성 가능 -> 사용자 설정이 필요함
- git config --global user.email "you@example.com" 
- git config --global user.name "you"
- code ~/.gitconfig 에서 수정 가능
- git commit 후에 i나 a 누르면 insert 모드로 변경 가능. esc를 통해 insert 모드에서 벗어날 수 있음 :wq를 치면 나가짐(write, quit)
  - git commit -m "메세지 남기기" : ""로 감싸서 하나의 string으로 만들고, 메세지를 남긴다
- 커밋 : 버전을 남기는 것이기 때문에 무엇을 어떻게 수정했는지에 대한 설명을 한다. 
- 커밋을 통해 버젼이 생긴 친구들은 git log를 통해 확인 가능(git init -> git add -> git commit -> git log 사이의 모든 단계에서 git status. 머리아플때 status. 피곤할때 status. 계속 찍어보기)
- git log --oneline --graph : 관계파악 가능, 한줄로 간략하게 출력