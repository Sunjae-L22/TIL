# DFS와 BFS 문제 유형 — 지문을 읽고 템플릿을 꺼내는 법

> 자기주도 학습 정리 (코딩 테스트 대비) · 정리일: 2026-08-25
> 블로그 발행본: https://it-study-2002.tistory.com/entry/DFS와-BFS-문제-유형
> 시리즈: [01 해시](0825_해시.md) · [02 DFS와 BFS 이론](0825_DFS와BFS_이론.md) · **03 DFS와 BFS 문제 유형**

DFS와 BFS를 다 이해했는데도 문제 앞에서 멈추는 순간이 있다. **원리를 아는 것과 지문을 읽고 어느 템플릿을 꺼낼지 아는 것은 별개**이기 때문이다. 시험장에서 필요한 건 "BFS는 큐를 쓴다"가 아니라 "이 문장이 보이면 다중 시작점 BFS다"라는 판별이다.

> 이 글은 [DFS와 BFS 완전정리](0825_DFS와BFS_이론.md) 편에서 이어진다. 탐색의 원리는 그쪽에서 다뤘고, 여기서는 문제 유형별 템플릿만 본다.

그래서 이 글은 원리를 다시 설명하지 않는다. **지문의 어떤 표현이 어떤 템플릿을 가리키는지**를 표로 먼저 세우고, 그 템플릿 여덟 개를 복사해 바로 쓸 수 있는 형태로 늘어놓는다. 실린 코드는 전부 작은 입력으로 실행해 정답을 확인한 것이다.

<br>

## 📖 이 글에서 다루는 내용

1. 지문에서 유형을 판별하는 신호표
2. 격자 탐색 기본형
3. 연결 요소 세기 — 덩어리를 몇 개인가
4. 최단 거리와 경로 복원
5. 다중 시작점 BFS — 동시에 퍼지는 것들
6. 상태 공간 BFS — 좌표만으로 부족할 때
7. 0-1 BFS — 가중치가 0과 1뿐일 때
8. 백트래킹 DFS — 모든 경우를 만들어 보기
9. 사이클 판정과 위상 정렬
10. 흔한 실수 모음

<br>

---

## 1. 지문에서 유형을 판별하는 신호표

탐색 문제는 겉모습이 다 비슷하다. 격자가 나오고, 이동이 나오고, 무언가를 세라고 한다. 하지만 **지문에는 거의 항상 유형을 확정해 주는 문장이 한 줄 들어 있다.** 그 한 줄만 잡으면 나머지는 템플릿 복사다.

> **[그림]** 지문에 나오는 표현별로 어떤 탐색 템플릿을 꺼내야 하는지 연결한 판별 매트릭스

| 지문에 이런 표현이 있으면 | 꺼낼 템플릿 |
|---|---|
| "최소 몇 번 이동", "최단 거리", "최소 시간" + **이동 비용이 전부 같다** | BFS + `dist` 배열 |
| "영역이 몇 개인가", "섬의 개수", "덩어리로 묶어라" | 연결 요소 세기 (이중 반복문 + 탐색) |
| "각 영역의 크기를 오름차순으로" | 연결 요소 + 크기 수집 후 정렬 |
| "동시에 퍼진다", "며칠이 걸리는가", "모두 익는 시간" | **다중 시작점 BFS** |
| "벽을 K개까지 부술 수 있다", "열쇠를 얻으면 문이 열린다" | **상태 공간 BFS** (`visited`에 차원 추가) |
| "이동 비용이 0 또는 1이다", "벽을 최소 몇 개 부수면" | **0-1 BFS** (`deque` 양끝 삽입) |
| "가능한 모든 경우", "순서가 다르면 다른 것으로 본다" | 백트래킹 DFS |
| "경로 자체를 출력하라" | BFS + `parent` 역추적 |
| "A를 하려면 B를 먼저 해야 한다" | 위상 정렬 |
| "순환 참조가 있는가", "돌아오는 길이 있는가" | 사이클 판정 DFS |
| 간선마다 비용이 **제각각 다르다** | BFS로는 안 된다 → 다익스트라 |

이 표의 마지막 줄이 특히 중요하다. BFS가 최단 거리를 보장하는 것은 **모든 간선의 비용이 같을 때뿐**이다. 이유는 2편에서 다뤘다. 비용이 5, 3, 7처럼 제각각이면 BFS는 틀린 답을 내고, 그건 예제에서는 잘 안 드러난다.

### 판별을 3단 질문으로 압축하기

표가 길게 느껴지면 아래 세 질문만 순서대로 던져도 대부분 갈린다.

```text
Q1. 최단(최소)을 묻는가?
     예  → BFS 계열   아니오 → DFS / 백트래킹 계열

Q2. 상태가 좌표만으로 표현되는가?
     예  → 2차원 visited   아니오 → visited에 차원을 추가

Q3. 출발점이 하나인가?
     예  → 일반 BFS   아니오 → 시작점을 전부 큐에 넣고 출발
```

> ➡️ **한 줄 요약**
> 최단이면 BFS, 모든 경우면 백트래킹, 덩어리면 연결 요소. 나머지는 이 셋의 변형이다.

<br>

---

## 2. 격자 탐색 기본형

탐색 문제의 8할은 2차원 격자다. 격자 문제는 **방향 배열 → 경계 검사 → 방문 검사 → 진행**이라는 네 줄 리듬이 항상 똑같다. 이 리듬을 손에 붙이는 게 먼저다.

> **[그림]** 상하좌우 네 방향 이동 배열과 경계 검사 방문 검사가 어떤 칸을 걸러내는지 보여주는 격자 도식

### 방향 배열

상하좌우 네 방향은 두 개의 배열로 표현한다.

```python
dx = [-1, 1, 0, 0]   # 위, 아래, 제자리, 제자리
dy = [0, 0, -1, 1]   # 제자리, 제자리, 왼쪽, 오른쪽
```

대각선까지 포함하는 8방향이면 원소를 여덟 개로 늘린다.

```python
dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]
```

> 💡 **왜 배열로 빼는가**
> `if`문 네 개로 상하좌우를 쓰면 같은 코드가 네 번 반복되고, 조건 하나를 고칠 때 네 군데를 다 고쳐야 한다. 방향 배열로 빼면 `for d in range(4)` 한 줄로 접히고, 8방향으로 바꿔야 할 때 배열만 갈아 끼우면 된다.

### 기본 템플릿 — BFS

```python
from collections import deque

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def bfs_grid(board, sx, sy):
    n, m = len(board), len(board[0])
    visited = [[False] * m for _ in range(n)]
    q = deque([(sx, sy)])
    visited[sx][sy] = True          # 시작점 방문 표시를 빠뜨리지 않는다
    count = 1
    while q:
        x, y = q.popleft()
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue            # 경계 밖
            if visited[nx][ny] or board[nx][ny] == 0:
                continue            # 이미 갔거나 갈 수 없는 칸
            visited[nx][ny] = True  # 큐에 넣을 때 표시한다
            count += 1
            q.append((nx, ny))
    return count
```

작은 입력으로 확인하면 이렇게 동작한다.

```python
board = [
    [1, 1, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 1, 1],
]

bfs_grid(board, 0, 0)   # 3  — 왼쪽 위 덩어리
bfs_grid(board, 2, 2)   # 3  — 오른쪽 아래 덩어리
```

### 같은 문제를 DFS로

큐를 스택으로 바꾸면 그대로 DFS가 된다. `popleft()`가 `pop()`으로 바뀐 것 하나뿐이다.

```python
def dfs_grid(board, sx, sy):
    n, m = len(board), len(board[0])
    visited = [[False] * m for _ in range(n)]
    stack = [(sx, sy)]
    visited[sx][sy] = True
    count = 1
    while stack:
        x, y = stack.pop()          # 여기만 다르다
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue
            if visited[nx][ny] or board[nx][ny] == 0:
                continue
            visited[nx][ny] = True
            count += 1
            stack.append((nx, ny))
    return count
```

> ✅ **덩어리 크기·존재 여부만 묻는다면 둘 중 아무거나**
> 방문한 칸 수를 세거나 도달 가능한지만 확인하는 문제라면 DFS와 BFS의 결과가 같다. 방문 순서만 다르다. **최단 거리를 물을 때만 BFS여야 한다.**

### 방문 배열 대신 set을 쓰는 경우

좌표 범위가 아주 넓거나 음수 좌표가 나오면 2차원 리스트를 만들 수 없다. 이때는 좌표 튜플을 원소로 하는 `set`을 쓴다.

```python
visited = set()
visited.add((x, y))

if (nx, ny) in visited:
    continue
```

튜플이 `set`의 원소가 될 수 있는 이유와 리스트는 왜 안 되는지는 [파이썬 해시 완전정리](0825_해시.md) 편에서 다뤘다. 격자 크기가 정해져 있다면 2차원 리스트가 상수 비용이 더 작으니, `set`은 어쩔 수 없을 때만 쓴다.

<br>

---

## 3. 연결 요소 세기 — 덩어리를 몇 개인가

"섬이 몇 개인가", "단지가 몇 개인가", "그림이 몇 개인가"는 전부 같은 문제다. **격자 전체를 이중 반복문으로 훑으면서, 아직 방문하지 않은 유효 칸을 만날 때마다 탐색을 한 번 시작한다.** 탐색을 시작한 횟수가 곧 덩어리 개수다.

> **[그림]** 이중 반복문이 격자를 훑다가 미방문 칸을 만날 때마다 탐색을 시작해 덩어리 하나씩 지워 나가는 과정

### 개수만 세기

```python
from collections import deque

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def count_islands(board):
    n, m = len(board), len(board[0])
    visited = [[False] * m for _ in range(n)]
    groups = 0
    for i in range(n):
        for j in range(m):
            if board[i][j] == 0 or visited[i][j]:
                continue
            groups += 1                     # 새 덩어리 발견
            q = deque([(i, j)])
            visited[i][j] = True
            while q:
                x, y = q.popleft()
                for d in range(4):
                    nx, ny = x + dx[d], y + dy[d]
                    if not (0 <= nx < n and 0 <= ny < m):
                        continue
                    if visited[nx][ny] or board[nx][ny] == 0:
                        continue
                    visited[nx][ny] = True
                    q.append((nx, ny))
    return groups
```

```python
board = [
    [1, 1, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 1, 1],
]
count_islands(board)   # 2
```

여기서 핵심은 **바깥 이중 반복문이 O(N×M)이지만 전체 복잡도는 여전히 O(N×M)**이라는 점이다. 각 칸은 방문 표시 덕분에 정확히 한 번만 큐에 들어간다. 바깥 반복문은 "아직 안 먹은 덩어리가 남았는지" 확인하는 역할일 뿐이다.

### 단지 번호 매기기 — 크기까지 함께

각 덩어리의 크기를 오름차순으로 출력하라는 변형이 잦다. `visited` 대신 **번호를 적는 배열**을 쓰면 방문 표시와 라벨링을 동시에 처리할 수 있다.

```python
def label_groups(board):
    n, m = len(board), len(board[0])
    label = [[0] * m for _ in range(n)]     # 0 = 미방문
    sizes = []
    for i in range(n):
        for j in range(m):
            if board[i][j] == 0 or label[i][j]:
                continue
            num = len(sizes) + 1            # 1번 단지부터
            label[i][j] = num
            q = deque([(i, j)])
            size = 1
            while q:
                x, y = q.popleft()
                for d in range(4):
                    nx, ny = x + dx[d], y + dy[d]
                    if not (0 <= nx < n and 0 <= ny < m):
                        continue
                    if label[nx][ny] or board[nx][ny] == 0:
                        continue
                    label[nx][ny] = num
                    size += 1
                    q.append((nx, ny))
            sizes.append(size)
    return sorted(sizes), label
```

```python
sizes, label = label_groups(board)
sizes
# [3, 3]

label
# [1, 1, 0, 0]
# [1, 0, 0, 2]
# [0, 0, 2, 2]
```

> 💡 **`visited`와 `label`을 하나로 합치기**
> 번호는 1부터 매기므로 `0`이 자연스럽게 "미방문"을 뜻한다. 배열 두 개를 관리하다가 한쪽만 갱신하는 실수가 사라지고, 나중에 "이 칸이 몇 번 단지인가"를 묻는 후속 질문에도 그대로 답할 수 있다.

### 대각선을 포함하는지 확인할 것

"그림의 개수" 유형에서는 4방향인지 8방향인지가 답을 완전히 갈라놓는다. 지문에 **"모서리가 닿아 있는 경우도 연결된 것으로 본다"** 같은 문장이 있으면 8방향이다. 방향 배열만 바꾸면 된다.

<br>

---

## 4. 최단 거리와 경로 복원

"최소 몇 칸을 지나야 하는가"는 BFS의 본진이다. 방법은 두 가지인데, **거리만 필요하면 `dist` 배열, 경로 자체가 필요하면 `parent` 배열**을 쓴다.

> **[그림]** 거리 배열이 층별로 채워지는 모습과 부모 배열을 거꾸로 따라가 경로를 복원하는 두 가지 방식

### 방식 1 — dist 배열

`visited`를 따로 두지 않고 **`dist`가 방문 표시를 겸한다.** `-1`이면 아직 안 간 칸이다. 배열 두 개를 관리하지 않아도 되니 실수가 줄어든다.

```python
from collections import deque

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def shortest(maze, start, goal):
    n, m = len(maze), len(maze[0])
    dist = [[-1] * m for _ in range(n)]     # -1 = 미방문
    sx, sy = start
    dist[sx][sy] = 0
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            return dist[x][y]
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue
            if dist[nx][ny] != -1 or maze[nx][ny] == 0:
                continue
            dist[nx][ny] = dist[x][y] + 1
            q.append((nx, ny))
    return -1                                # 도달 불가
```

```python
maze = [
    [1, 0, 1, 1, 1],
    [1, 1, 1, 0, 1],
    [0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1],
]
shortest(maze, (0, 0), (3, 4))   # 7
```

> ⚠️ **"이동 횟수"인가 "지나는 칸 수"인가**
> 위 코드는 시작 칸을 0으로 두므로 **이동 횟수**를 센다. 시작 칸과 도착 칸을 모두 포함한 **칸 수**를 요구하는 문제라면 `dist[sx][sy] = 1`로 시작하거나 마지막에 `+1` 해야 한다. 답이 정확히 1씩 어긋난다면 십중팔구 이 지점이다.

### 방식 2 — parent 역추적

경로를 출력해야 하면 각 칸에 **"어디서 왔는지"**를 적어 둔다. 도착점에서 시작점까지 거꾸로 따라간 뒤 뒤집으면 경로가 나온다.

```python
def shortest_path(maze, start, goal):
    n, m = len(maze), len(maze[0])
    parent = [[None] * m for _ in range(n)]
    visited = [[False] * m for _ in range(n)]
    sx, sy = start
    visited[sx][sy] = True
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue
            if visited[nx][ny] or maze[nx][ny] == 0:
                continue
            visited[nx][ny] = True
            parent[nx][ny] = (x, y)          # 어디서 왔는지 기록
            q.append((nx, ny))

    gx, gy = goal
    if not visited[gx][gy]:
        return []                            # 도달 불가

    path, cur = [], goal
    while cur is not None:                   # 시작점의 parent는 None
        path.append(cur)
        cur = parent[cur[0]][cur[1]]
    path.reverse()
    return path
```

```python
shortest_path(maze, (0, 0), (3, 4))
# [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2), (3, 3), (3, 4)]
# len(path) - 1 == 7  ← dist 방식의 답과 일치한다
```

| 필요한 것 | 쓸 배열 | 메모리 |
|---|---|---|
| 거리(횟수)만 | `dist` 하나 (방문 표시 겸용) | 정수 배열 1개 |
| 경로 전체 | `parent` + `visited` | 좌표 배열 1개 + 불리언 배열 1개 |
| 거리와 경로 둘 다 | `dist` + `parent` | 정수 배열 1개 + 좌표 배열 1개 |

> 💡 **`while cur is not None` 을 `while cur:` 로 쓰면 안 된다**
> 좌표 `(0, 0)`은 파이썬에서 참(truthy)이지만, 습관적으로 `while cur:`라고 쓰면 튜플이 비어 있을 때만 멈춘다는 뜻이 되어 의도가 흐려진다. 더 위험한 건 정점 번호를 쓰는 그래프 버전이다. `parent[v]`가 `0`인 순간 반복문이 조기 종료되어 경로 앞부분이 통째로 잘린다. **`is not None`으로 명시한다.**

<br>

---

## 5. 다중 시작점 BFS — 동시에 퍼지는 것들

"익은 토마토가 사방으로 퍼진다", "불이 여러 곳에서 동시에 번진다" 유형이다. 여기서 초보자가 가장 흔히 하는 선택은 **시작점마다 BFS를 한 번씩 돌려 최솟값을 구하는 것**인데, 느리기만 한 게 아니라 문제의 의미와도 다르다.

> **[그림]** 시작점 하나씩 N번 BFS를 도는 방식과 시작점을 전부 큐에 넣고 한 번에 퍼뜨리는 방식의 비교

### 왜 한 번에 넣어야 하는가

BFS는 큐에 처음부터 들어 있던 원소들을 **같은 층(거리 0)으로 취급한다.** 시작점을 전부 큐에 넣고 출발하면, 각 칸은 자연히 "가장 가까운 시작점으로부터의 거리"로 채워진다. 별도의 최솟값 비교가 필요 없다.

| 방식 | 복잡도 | 의미 |
|---|---|---|
| 시작점마다 BFS를 K번 | O(K × N × M) | 각 시작점 기준 거리를 K장 만들고 최솟값 합성 |
| **시작점을 전부 큐에 넣고 1번** | **O(N × M)** | 한 번의 전파로 최소 거리가 바로 나온다 |

시작점이 1만 개인 격자에서 이 차이는 통과와 시간 초과를 가른다.

### 템플릿

```python
from collections import deque

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def ripen(box):
    """1=익음, 0=안 익음, -1=빈 칸. 전부 익는 데 걸리는 일수."""
    n, m = len(box), len(box[0])
    q = deque()
    unripe = 0
    for i in range(n):
        for j in range(m):
            if box[i][j] == 1:
                q.append((i, j))       # 시작점을 전부 큐에 넣는다
            elif box[i][j] == 0:
                unripe += 1
    if unripe == 0:
        return 0                       # 처음부터 다 익어 있다

    days = 0
    while q:
        x, y = q.popleft()
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue
            if box[nx][ny] != 0:
                continue               # 빈 칸이거나 이미 익음
            box[nx][ny] = box[x][y] + 1
            days = max(days, box[nx][ny] - 1)
            unripe -= 1
            q.append((nx, ny))
    return days if unripe == 0 else -1
```

격자를 그대로 거리 배열로 재활용한 형태다. 익은 칸은 `1`이므로 `box[nx][ny] = box[x][y] + 1`이 곧 `거리 + 1`이 되고, 마지막에 `-1`을 해서 일수로 환산한다.

```python
ripen([[0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1]])          # 8

ripen([[0, -1, 0, 0, 0],
       [0,  0, 0, 0, 0],
       [0,  0, 0, 0, 1]])            # 6

ripen([[1, 1],
       [1, 1]])                      # 0  — 처음부터 다 익었다

ripen([[0, -1],
       [-1, 1]])                     # -1 — 영영 못 익는 칸이 있다
```

> ⚠️ **세 가지 예외를 반드시 따로 처리한다**
> ① 처음부터 전부 익어 있으면 `0`. ② 벽에 막혀 못 닿는 칸이 남으면 `-1`. ③ 시작점이 하나도 없으면 남은 칸이 있는 한 `-1`. 이 셋 중 하나라도 빠지면 예제는 통과하고 제출에서 틀린다. 위 코드는 **남은 개수(`unripe`)를 세는 방식**으로 세 경우를 한꺼번에 처리한다. 마지막에 격자를 다시 훑어 `0`이 남았는지 확인하는 방법도 있지만, 카운터 쪽이 한 번 덜 훑는다.

### 응용 — 불과 사람이 동시에 움직일 때

불이 번지는 BFS를 먼저 끝까지 돌려 `fire_time` 배열을 만들고, 그다음 사람의 BFS를 돌리며 **`사람 도착 시간 < 불 도착 시간`인 칸만 통과**시키는 2단 구성이 정석이다. 두 BFS를 한 큐에서 섞으려 하면 순서 제어가 어려워진다.

<br>

---

## 6. 상태 공간 BFS — 좌표만으로 부족할 때

여기서부터가 진짜 갈림길이다. **`visited[x][y]`가 부족해지는 문제**가 있다. 같은 칸에 와도 "어떤 상태로 왔느냐"에 따라 앞으로 할 수 있는 일이 달라지기 때문이다.

> **[그림]** 좌표만 기록하는 2차원 방문 배열과 벽을 부순 횟수까지 기록하는 3차원 방문 배열의 층 구조 비교

### 문제의 냄새

- 벽을 **K개까지** 부술 수 있다
- 열쇠를 얻으면 대응하는 문을 지날 수 있다
- 낮과 밤에 따라 이동 규칙이 다르다
- 특정 아이템을 쓰면 한 번 순간이동할 수 있다

공통점은 **"같은 칸이라도 조건이 다르면 다른 칸"** 이라는 것이다. 벽을 하나도 안 부수고 (3, 4)에 도착한 것과, 이미 두 개를 부수고 (3, 4)에 도착한 것은 완전히 다른 처지다. 앞의 경우는 앞으로도 벽을 부술 수 있고 뒤의 경우는 못 부술 수 있다.

> ✅ **해법은 하나다: `visited`에 차원을 늘린다**
> `visited[x][y]` → `visited[x][y][k]`. 상태를 정의하는 순간 문제의 절반이 풀린다.

### 템플릿 — 벽을 K개까지 부수기

```python
from collections import deque

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def break_wall(grid, K):
    """0=빈 칸, 1=벽. 벽을 K개까지 부수며 (0,0)에서 끝까지 가는 최소 칸 수."""
    n, m = len(grid), len(grid[0])
    visited = [[[False] * (K + 1) for _ in range(m)] for _ in range(n)]
    visited[0][0][0] = True
    q = deque([(0, 0, 0, 1)])            # x, y, 부순 횟수, 지나온 칸 수
    while q:
        x, y, k, dist = q.popleft()
        if x == n - 1 and y == m - 1:
            return dist
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue
            if grid[nx][ny] == 0 and not visited[nx][ny][k]:
                visited[nx][ny][k] = True
                q.append((nx, ny, k, dist + 1))
            elif grid[nx][ny] == 1 and k < K and not visited[nx][ny][k + 1]:
                visited[nx][ny][k + 1] = True
                q.append((nx, ny, k + 1, dist + 1))
    return -1
```

```python
demo = [
    [0, 1, 0],
    [0, 1, 0],
    [0, 1, 0],
]

break_wall(demo, 0)   # -1  — 가운데 벽 기둥에 막힌다
break_wall(demo, 1)   # 5   — 벽 하나만 부수면 5칸
break_wall(demo, 2)   # 5   — 더 부술 수 있어도 최단은 그대로
```

3차원 배열 생성 순서를 헷갈리기 쉬운데, 안쪽부터 읽으면 된다. `[False] * (K+1)`이 가장 안쪽 차원이고, 그걸 `m`번 반복해 한 행을, 다시 `n`번 반복해 격자를 만든다.

### 상태 정의가 곧 문제 해결이다

상태를 어떻게 잡느냐가 전부다. 몇 가지 예를 보면 감이 온다.

| 문제 상황 | 상태 정의 | 배열 크기 |
|---|---|---|
| 벽을 K개까지 부순다 | `(x, y, 부순 개수)` | N × M × (K+1) |
| 열쇠 6종을 모은다 | `(x, y, 열쇠 비트마스크)` | N × M × 64 |
| 낮/밤이 번갈아 온다 | `(x, y, 시각 mod 2)` | N × M × 2 |
| 말처럼 K번 점프할 수 있다 | `(x, y, 남은 점프 횟수)` | N × M × (K+1) |

열쇠 문제에서 비트마스크를 쓰는 이유는 **"어떤 열쇠들을 가졌는가"라는 집합을 정수 하나로 압축하기 위해서**다. 열쇠 6종이면 상태는 `0`부터 `63`까지 64가지다.

```python
keys = 0
keys |= (1 << 2)          # 2번 열쇠 획득
if keys & (1 << 2):       # 2번 열쇠를 가졌는가
    ...
```

> ⚠️ **상태 공간 크기를 먼저 계산한다**
> N=1,000, M=1,000, K=10이면 상태 수는 1,000만 개가 넘는다. 파이썬에서 3차원 리스트로 잡으면 메모리가 위험하다. 상태 하나가 늘 때마다 배열이 통째로 곱해진다는 걸 기억하고, **차원을 늘리기 전에 곱셈부터 해 본다.**

<br>

---

## 7. 0-1 BFS — 가중치가 0과 1뿐일 때

간선 비용이 제각각이면 다익스트라를 써야 한다. 그런데 **비용이 0 아니면 1인 특수한 경우**에는 우선순위 큐 없이 `deque`만으로 같은 결과를 얻을 수 있다.

> **[그림]** 비용 0인 이동은 덱 앞쪽에 비용 1인 이동은 뒤쪽에 넣어 우선순위 큐 없이 최단 거리를 구하는 원리

### 원리 한 문단

일반 BFS가 최단 거리를 보장하는 건 큐가 항상 거리 순으로 정렬돼 있기 때문이다. 비용 0인 간선을 타면 거리가 그대로이므로 **큐의 맨 앞에 넣어야** 정렬이 유지되고, 비용 1이면 뒤에 넣으면 된다. 그래서 `deque`의 양끝 삽입만으로 정렬 상태가 유지된다.

```python
if cost == 0:
    dq.appendleft((nx, ny))   # 거리가 그대로 → 맨 앞
else:
    dq.append((nx, ny))       # 거리가 1 증가 → 맨 뒤
```

### 템플릿 — 벽을 최소 몇 개 부수면 도달하는가

```python
from collections import deque

dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]

def min_walls(grid):
    """0=빈 칸, 1=벽. (0,0)에서 끝까지 가며 부숴야 하는 벽의 최소 개수."""
    n, m = len(grid), len(grid[0])
    INF = float("inf")
    dist = [[INF] * m for _ in range(n)]
    dist[0][0] = grid[0][0]
    dq = deque([(0, 0)])
    while dq:
        x, y = dq.popleft()
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not (0 <= nx < n and 0 <= ny < m):
                continue
            cost = grid[nx][ny]              # 벽이면 1, 빈 칸이면 0
            if dist[x][y] + cost < dist[nx][ny]:
                dist[nx][ny] = dist[x][y] + cost
                if cost == 0:
                    dq.appendleft((nx, ny))
                else:
                    dq.append((nx, ny))
    return dist[n - 1][m - 1]
```

```python
min_walls([[0, 1, 0],
           [0, 1, 0],
           [0, 1, 0]])          # 1

min_walls([[0, 1, 1, 0],
           [0, 1, 1, 0],
           [0, 0, 1, 0]])       # 1
```

같은 입력 400개를 무작위로 만들어 다익스트라 결과와 대조했을 때 전부 일치했다.

> ⚠️ **일반 BFS와 달리 방문 표시로 끝내지 않는다**
> 0-1 BFS는 **한 정점이 여러 번 큐에 들어갈 수 있다.** 나중에 더 짧은 경로가 발견되면 거리를 갱신하고 다시 넣어야 한다. 그래서 `visited` 불리언 대신 **`dist` 값 비교(`더 작으면 갱신`)로 진행 여부를 정한다.** 일반 BFS 템플릿을 그대로 가져와 `visited`로 막으면 틀린 답이 나온다.

| 상황 | 자료구조 | 복잡도 |
|---|---|---|
| 모든 간선 비용이 같다 | `deque` (한쪽 삽입) | O(V+E) |
| 비용이 0 또는 1 | `deque` (**양끝 삽입**) | O(V+E) |
| 비용이 제각각(양수) | `heapq` (다익스트라) | O(E log V) |

<br>

---

## 8. 백트래킹 DFS — 모든 경우를 만들어 보기

"가능한 모든 경우의 수", "N개 중 M개를 고르는 모든 방법"은 최단 거리와 정반대 성격이다. **답을 찾는 게 아니라 후보를 전부 생성해야 한다.** 여기서는 재귀 DFS가 압도적으로 편하다.

> **[그림]** 재귀가 한 칸 내려가며 후보를 쌓고 되돌아 나오면서 표시를 되돌리는 백트래킹 트리 구조

### 되돌리기의 위치가 전부다

백트래킹의 뼈대는 네 줄이다.

```text
1. 선택한다      → used[i] = True, path.append(...)
2. 내려간다      → dfs(depth + 1)
3. 되돌린다      → path.pop(), used[i] = False
4. 다음 후보로   → 반복문의 다음 i
```

3번을 빠뜨리면 이전 가지의 선택이 다음 가지에 그대로 남아 결과가 엉킨다. **되돌리기는 재귀 호출 바로 다음 줄**이라고 외워 두면 위치를 헷갈릴 일이 없다.

### 순열 — 순서가 다르면 다른 것

```python
def permutations(arr, r):
    n = len(arr)
    used = [False] * n
    path, result = [], []

    def dfs(depth):
        if depth == r:
            result.append(path[:])       # 사본을 넣는다
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            path.append(arr[i])
            dfs(depth + 1)
            path.pop()                   # 되돌리기
            used[i] = False
    dfs(0)
    return result
```

```python
permutations([1, 2, 3], 2)
# [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]
```

`itertools.permutations`의 결과와 순서까지 동일하다.

> ⚠️ **`result.append(path)`가 아니라 `result.append(path[:])`**
> `path`는 재귀가 진행되면서 계속 바뀌는 **같은 리스트 객체**다. 사본을 뜨지 않고 넣으면 결과 리스트에 같은 객체가 여러 번 들어가고, 탐색이 끝난 뒤에는 전부 빈 리스트가 되어 있다. `path[:]`, `list(path)`, `path.copy()` 중 아무거나 쓰면 된다. **백트래킹에서 가장 자주 나오는 버그다.**

### 조합 — 순서를 무시할 때

순열과 딱 한 군데가 다르다. `used` 배열 대신 **`start` 인덱스**를 넘겨 이미 지나간 원소를 다시 보지 않는다.

```python
def combinations(arr, r):
    n = len(arr)
    path, result = [], []

    def dfs(start, depth):
        if depth == r:
            result.append(path[:])
            return
        for i in range(start, n):        # start부터 — 뒤로 안 돌아간다
            path.append(arr[i])
            dfs(i + 1, depth + 1)        # i+1을 넘긴다
            path.pop()
    dfs(0, 0)
    return result
```

```python
combinations([1, 2, 3, 4], 2)
# [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
```

중복 조합이 필요하면 `dfs(i + 1, ...)`을 `dfs(i, ...)`로 바꾼다. 같은 원소를 다시 고를 수 있게 된다.

| 유형 | 진행 방식 | 개수 |
|---|---|---|
| 순열 | `used` 배열 + 매번 0부터 | nPr |
| 중복 순열 | `used` 없이 매번 0부터 | n^r |
| 조합 | `start` 인덱스 + `dfs(i+1)` | nCr |
| 중복 조합 | `start` 인덱스 + `dfs(i)` | (n+r-1)Cr |

### 가지치기 — 백트래킹의 존재 이유

모든 경우를 다 만들면 순열은 금세 폭발한다. `10!`은 360만이고 `12!`는 4억이 넘는다. 백트래킹이 완전 탐색과 다른 점은 **가망 없는 가지를 내려가기 전에 잘라내는 것**이다.

N-Queens가 교과서적인 예다. 퀸을 놓을 때마다 열과 두 방향 대각선이 이미 점유됐는지 확인해, 안 되면 아예 내려가지 않는다.

```python
def n_queens(n):
    cols = [False] * n
    diag1 = [False] * (2 * n - 1)        # r + c 가 같으면 같은 대각선
    diag2 = [False] * (2 * n - 1)        # r - c 가 같으면 같은 대각선
    count = 0

    def dfs(row):
        nonlocal count
        if row == n:
            count += 1
            return
        for c in range(n):
            d1, d2 = row + c, row - c + n - 1
            if cols[c] or diag1[d1] or diag2[d2]:
                continue                 # 가지치기
            cols[c] = diag1[d1] = diag2[d2] = True
            dfs(row + 1)
            cols[c] = diag1[d1] = diag2[d2] = False
    dfs(0)
    return count
```

```python
[n_queens(n) for n in range(1, 9)]
# [1, 0, 0, 2, 10, 4, 40, 92]
```

`n=8`에서 92가 나오면 제대로 구현된 것이다. 한 행에 퀸을 하나씩만 놓는다고 고정했으므로 행 검사는 필요 없고, 열과 대각선 두 방향만 보면 된다. 대각선 인덱스에서 `+ n - 1`을 더하는 이유는 `row - c`가 음수가 될 수 있어 배열 인덱스로 못 쓰기 때문이다.

> 💡 **가지치기 조건은 "지금까지의 선택으로 확정된 사실"이어야 한다**
> 아직 정해지지 않은 미래를 근거로 자르면 정답까지 잘라낸다. 배낭 문제에서 "남은 무게로는 최대 이만큼밖에 못 담는다"처럼 **상한을 계산해 자르는 것**은 안전하지만, "이쯤 하면 안 될 것 같다"는 감으로 자르면 틀린다.

<br>

---

## 9. 사이클 판정과 위상 정렬

격자가 아니라 **작업 순서·의존 관계**가 나오는 문제 계열이다. "A를 하려면 B를 먼저 끝내야 한다"는 문장이 보이면 여기다.

> **[그림]** 진입 차수가 0인 정점부터 꺼내며 순서를 만들고 사이클이 있으면 정점이 남는 위상 정렬 과정

### 사이클 판정 — 3색 DFS

방향 그래프에서 사이클을 찾을 때는 정점을 세 상태로 관리한다. **아직 안 봄 / 지금 탐색 중 / 다 끝남**이다. 탐색 중인 정점으로 되돌아오면 그게 사이클이다.

```python
def has_cycle(graph, n):
    state = [0] * n                 # 0=미방문, 1=탐색 중, 2=완료

    def dfs(v):
        state[v] = 1
        for nxt in graph[v]:
            if state[nxt] == 1:     # 탐색 중인 정점으로 되돌아왔다
                return True
            if state[nxt] == 0 and dfs(nxt):
                return True
        state[v] = 2
        return False

    return any(state[v] == 0 and dfs(v) for v in range(n))
```

```python
dag = {0: [1, 2], 1: [3], 2: [3], 3: []}
cyc = {0: [1], 1: [2], 2: [0], 3: []}

has_cycle(dag, 4)   # False
has_cycle(cyc, 4)   # True
```

> ⚠️ **완료(2)와 탐색 중(1)을 구분하지 않으면 오답이 난다**
> 단순 `visited` 하나로 판정하면 위 `dag` 예시에서 정점 3을 두 번 만나 사이클로 오인한다. 갈래가 갈라졌다 다시 합쳐지는 것과 되돌아오는 것은 다르다. **무방향 그래프**라면 상태 대신 "직전에 온 정점(parent)"을 넘겨 그쪽으로 돌아가는 것만 예외 처리한다.

### 위상 정렬 — 진입 차수 0부터

의존 관계를 만족하는 작업 순서를 만드는 알고리즘이다. **들어오는 간선이 하나도 없는 정점(진입 차수 0)**부터 꺼내고, 꺼낼 때마다 그 정점이 가리키던 정점들의 진입 차수를 줄인다. BFS와 구조가 똑같다.

```python
from collections import deque

def topo_sort(graph, indeg, n):
    q = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for nxt in graph[v]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return order if len(order) == n else []   # 빈 리스트면 사이클
```

```python
def indegrees(graph, n):
    d = [0] * n
    for v in graph:
        for nxt in graph[v]:
            d[nxt] += 1
    return d

topo_sort(dag, indegrees(dag, 4), 4)   # [0, 1, 2, 3]
topo_sort(cyc, indegrees(cyc, 4), 4)   # []  — 사이클이 있다
```

> ✅ **위상 정렬은 사이클 판정을 공짜로 준다**
> 결과의 길이가 정점 수보다 짧으면 남은 정점들이 서로 물고 물리는 사이클을 이루고 있다는 뜻이다. "작업을 전부 끝낼 수 있는가"를 묻는 문제는 이 한 줄로 답이 나온다. 사이클 판정만 필요하다면 3색 DFS와 위상 정렬 중 편한 쪽을 쓰면 된다.

<br>

---

## 10. 흔한 실수 모음

여기 있는 여섯 개는 전부 **예제는 통과하고 제출에서 터지는** 종류다. 에러 메시지가 안 나오거나, 나와도 원인과 멀리 떨어져 있다.

> **[그림]** 방문 처리 시점 리스트 팝 재귀 깊이 인덱스 뒤집기 등 탐색 문제의 흔한 실수 여섯 가지 정리

### 1) 방문 처리를 꺼낼 때 한다

가장 흔하고 가장 조용한 실수다. 결과는 맞는데 시간만 터진다.

```python
# 위험 — 꺼낼 때 표시
while q:
    v = q.popleft()
    if visited[v]:
        continue
    visited[v] = True
    ...

# 정석 — 넣을 때 표시
visited[start] = True
q = deque([start])
while q:
    v = q.popleft()
    for nxt in graph[v]:
        if not visited[nxt]:
            visited[nxt] = True
            q.append(nxt)
```

꺼낼 때 표시하면 아직 처리되지 않은 정점이 여러 경로를 통해 **큐에 중복으로 쌓인다.** 정점 12개짜리 완전 그래프로 재어 보면 큐에 들어간 총 횟수가 12번 대 67번이었다. 정점 수가 늘수록 격차는 급격히 벌어진다.

### 2) `deque` 대신 `list.pop(0)`

```python
q = []
q.pop(0)      # O(N) — 뒤의 원소를 전부 한 칸씩 당긴다

from collections import deque
q = deque()
q.popleft()   # O(1)
```

리스트의 `pop(0)`은 앞을 빼는 순간 나머지 전체를 이동시킨다. 10만 개를 전부 빼는 데 걸린 시간을 재 보면 `deque`보다 수십 배 느리다(측정 환경에서 약 90배). BFS 안에 들어가면 그대로 시간 초과다. **`from collections import deque`는 BFS를 쓰겠다고 마음먹은 순간 같이 친다.**

### 3) 재귀 깊이

파이썬의 기본 재귀 한계는 1,000이다. 격자가 100×100만 되어도 한 줄로 이어진 경로에서 1만 번을 내려갈 수 있다.

```python
import sys
sys.setrecursionlimit(10 ** 6)
```

다만 이건 파이썬 인터프리터의 한계를 푸는 것이지 시스템 스택까지 늘리는 건 아니라서, 너무 깊으면 세그멘테이션 오류로 죽는다. **깊이가 정말 깊을 수 있는 문제라면 처음부터 스택을 쓰는 반복문 DFS로 짜는 게 안전하다.**

### 4) 격자 인덱스를 뒤집는다

파이썬에서 2차원 리스트는 `board[행][열]`이다. 그런데 좌표를 `(x, y)`라고 부르는 순간 머릿속에서 x가 가로가 되어 버린다.

```python
# 흔한 사고
board[x][y]   # x를 세로로 쓸 것인가 가로로 쓸 것인가
```

정사각 격자에서는 뒤집어도 에러가 안 나고 답만 틀린다. 직사각형이면 그나마 `IndexError`로 알려준다.

> ✅ **이름으로 못을 박는다**
> `(x, y)` 대신 `(r, c)` 또는 `(row, col)`로 쓰고, 격자 접근은 항상 `board[r][c]`로 통일한다. 방향 배열도 `dr = [-1, 1, 0, 0]`, `dc = [0, 0, -1, 1]`로 이름을 맞춘다. 이 글의 템플릿은 관행을 따라 `dx`/`dy`를 썼지만, **`dx`가 행 방향이라는 점**을 매번 기억해야 한다면 처음부터 `dr`/`dc`가 낫다.

### 5) 시작점 방문 표시 누락

```python
q = deque([(sx, sy)])
# visited[sx][sy] = True 를 안 썼다
```

시작점 표시를 빼면 이웃을 탐색하다가 시작점으로 되돌아오고, 그 시작점이 다시 이웃을 큐에 넣는다. 격자에서는 무한 루프까지는 잘 안 가지만 **거리 계산이 어긋나고 방문 횟수가 부풀어 오른다.** `dist` 배열 방식(`dist[sx][sy] = 0`)을 쓰면 방문 표시와 거리 초기화가 한 줄로 합쳐져 이 실수가 구조적으로 사라진다.

### 6) 사본을 뜨지 않고 결과에 담기

백트래킹 절에서 짚은 `result.append(path[:])` 문제다. 격자 문제에서도 같은 형태로 나온다.

```python
new_board = board[:]          # 얕은 복사 — 안쪽 행은 그대로 공유된다
new_board = [row[:] for row in board]   # 2차원은 이렇게
```

`board[:]`는 바깥 리스트만 새로 만들고 각 행은 원본과 같은 객체를 가리킨다. 시뮬레이션 문제에서 격자를 복사해 놓고 원본이 같이 변하는 사고가 여기서 난다.

| 실수 | 증상 | 처방 |
|---|---|---|
| 꺼낼 때 방문 표시 | 답은 맞고 시간 초과 | 큐에 **넣을 때** 표시 |
| `list.pop(0)` | 시간 초과 | `deque.popleft()` |
| 재귀 깊이 | `RecursionError` 또는 런타임 에러 | `setrecursionlimit` 또는 반복문 DFS |
| 인덱스 뒤집기 | 답만 틀림 (에러 없음) | `(r, c)` 이름 통일 |
| 시작점 표시 누락 | 거리 +1 어긋남, 중복 방문 | `dist[sx][sy] = 0` 방식 |
| 얕은 복사 | 원본이 같이 바뀜 | `[row[:] for row in board]` |

<br>

---

## ✅ 핵심 요약

| 유형 | 신호와 템플릿 |
|---|---|
| **격자 기본형** | 방향 배열 → 경계 검사 → 방문 검사 → 진행. `popleft()`면 BFS, `pop()`이면 DFS |
| **연결 요소** | 이중 반복문으로 훑다가 미방문 유효 칸에서 탐색 시작. 시작 횟수 = 덩어리 수 |
| **단지 번호** | `visited` 대신 번호 배열. `0`이 곧 미방문 |
| **최단 거리** | `dist` 배열이 방문 표시를 겸한다. `-1` = 미방문 |
| **경로 복원** | `parent[nx][ny] = (x, y)` 기록 후 역추적. 종료 조건은 `is not None` |
| **다중 시작점** | 시작점을 **전부 큐에 넣고** 한 번만 돈다. N번 도는 것보다 K배 빠르다 |
| **상태 공간** | 같은 칸도 조건이 다르면 다른 칸. `visited[x][y][k]`. 차원 늘리기 전에 곱셈부터 |
| **0-1 BFS** | 비용 0이면 `appendleft`, 1이면 `append`. `visited`가 아니라 `dist` 비교로 진행 |
| **백트래킹** | 선택 → 재귀 → **되돌리기** → 다음. 결과에는 반드시 `path[:]` 사본 |
| **순열 vs 조합** | `used` 배열이면 순열, `start` 인덱스면 조합 |
| **위상 정렬** | 진입 차수 0부터 꺼낸다. 결과 길이가 짧으면 사이클 |
| **BFS의 한계** | 간선 비용이 제각각이면 BFS는 틀린다. 다익스트라로 간다 |

<br>

> 이것으로 3편이 끝났다. 해시로 방문 처리를 빠르게 만들고, 탐색의 원리를 세우고, 유형별 템플릿을 손에 붙이는 순서였다. 막히는 문제를 만나면 1번 절의 신호표로 돌아와 지문의 한 문장을 다시 찾아보면 된다.

<br>

## 🔗 참고 자료

- [파이썬 공식 문서 — collections.deque](https://docs.python.org/ko/3/library/collections.html#collections.deque)
- [파이썬 공식 문서 — itertools](https://docs.python.org/ko/3/library/itertools.html)
- [파이썬 공식 문서 — sys.setrecursionlimit](https://docs.python.org/ko/3/library/sys.html#sys.setrecursionlimit)
- [파이썬 시간 복잡도 정리 (Python Wiki)](https://wiki.python.org/moin/TimeComplexity)
