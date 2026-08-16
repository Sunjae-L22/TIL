# Python 핵심문법 & API, JSON, LLM

> 출처: `0804_AI Python(1)_Python 핵심문법.pdf` (총 68페이지) · 정리일: 2026-08-14
> 페이지 표기는 PDF 물리 페이지 기준 (슬라이드 인쇄 번호와 일치).

## 한눈에 보기

- AI가 짜준 코드의 환각(Hallucination)을 **읽고 검증**하기 위한 최소한의 문법 (p.3)
- `5 == "5"`는 왜 False이고, 빈 리스트는 왜 `if not scores`로 검사하는가
- `sort()`/`sorted()`, `append()`의 반환값, `dict["키"]`/`get()` — 반환값 함정 3종
- requests로 GET 요청 → `status_code` 확인 → `json()` 파싱 → 중첩 접근의 표준 흐름
- 네트워크 예외 4종을 원인별로 잡는 법, LLM API 요청·응답 구조, API 키를 환경 변수로 관리하는 이유

## 목차

1. [변수와 자료형](#변수와-자료형) (p.3-20)
2. [조건문, 반복문, 함수](#조건문-반복문-함수) (p.21-34)
3. [API, HTTP, requests 기초](#api-http-requests-기초) (p.35-44)
4. [JSON 파싱과 LLM 연결](#json-파싱과-llm-연결) (p.45-58)

---

## 변수와 자료형

도입 (p.3) — AI는 확률로 그럴듯한 답을 만드는 모델이라 환각이 생길 수 있고, **읽고 검증하지 못하면 틀린 코드를 그대로 쓰게 된다.** 이 강의 전체의 전제.

### 기초 압축 (p.5-10)

변수는 데이터를 저장하는 공간, `=`는 오른쪽 값을 왼쪽 변수에 담는 **할당**(수학의 등호와 다름). 변수명은 영문/`_`로 시작(숫자 시작 불가), 예약어(`if`, `for`, `True`) 불가. `type()`으로 자료형 확인 — `type("5")` → `<class 'str'>`.

| 자료형 | 예시 | 비고 |
|---|---|---|
| `int` | `10, -3, 0` | Python의 int는 **크기 제한 없음** |
| `float` | `3.14, -0.5` | `/` 나누기 결과는 항상 float |
| `str` | `"안녕", "AI"` | `5`(int)와 `"5"`(str)는 다른 값 |
| `bool` | `True, False` | 대문자 시작 |

연산·형 변환은 `age = 27` 기준 (p.9-10):

| 연산 | 결과 | 형 변환 | 결과 |
|---|---|---|---|
| `age / 2` | `13.5` (float) | `int("27")` | `27` |
| `age // 2` | `13` (몫) | `int(3.14)` | `3` — **소수점 아래 버림**(반올림 아님) |
| `age % 2` | `1` (나머지) | `str(27)` | `"27"` |
| `age ** 2` | `729` (제곱) | `float(27)` | `27.0` |

숫자+문자열 합치기: `"김싸피" + str(27) + "살"` 또는 f-string `f"김싸피 {27}살"` (p.10).

### list와 dict (p.11-15, 18)

| 구분 | list | dict |
|---|---|---|
| 모양 | `[v, v, v]` | `{k: v, k: v}` |
| 찾는 법 | 순서(인덱스, 0부터) | 이름(key, 중복 불가) |
| 언제 | 순서가 있는 데이터 (점수 목록) | 이름표가 붙은 데이터 (한 사람 정보) |

```python
scores = [90, 85, 70, 60, 50]
scores[0]    # 90 (앞에서부터)
scores[-1]   # 50 (뒤에서부터) — 길이를 몰라도 마지막 접근
scores[0:3]  # [90, 85, 70] — 끝 인덱스 3은 포함하지 않음
scores[::2]  # [90, 70, 50] — 두 칸 간격
```

둘은 서로 중첩 가능 — `students[0]["name"]`처럼 리스트 인덱스로 들어간 뒤 dict 키로 접근한다. 학생 명단이나 **API 응답** 표현에 쓰는 구조 (p.18).

### list 메서드 — 반환값이 함정 (p.16)

```python
scores = [90, 85, 70]
scores.append(60)      # [90, 85, 70, 60], 마지막에 60 추가
scores.insert(1, 95)   # [90, 95, 85, 70, 60], 인덱스 1에 95 삽입
scores.pop()           # [90, 95, 85, 70], 마지막 값을 제거하고 60 반환
scores.pop(1)          # [90, 85, 70], 인덱스 1의 값을 제거하고 95 반환
scores.remove(85)      # [90, 70], 값이 85인 항목 제거
scores = [70, 90, 60, 85]
scores.sort()          # [60, 70, 85, 90], 기존 리스트를 직접 정렬
print(sorted(scores))  # [60, 70, 85, 90], 정렬된 새로운 리스트 반환
```

> **주의** — `append()`는 리스트를 수정하고 **None을 반환**하므로 `scores = scores.append(60)`처럼 결과를 다시 저장하면 안 된다 (p.67에서 명시적으로 경고). `sort()`도 제자리 수정이라 반환값을 받으면 None이다.

### dict 메서드 — `[]` vs `get()` (p.17)

```python
person = {"name": "김싸피", "age": 27, "job": "학생"}
print(person["name"])               # "김싸피", 키가 없으면 KeyError 발생
print(person.get("name"))           # "김싸피", 키가 없으면 None 반환
print(person.get("hobby", "없음"))  # "없음", 키가 없으면 지정한 기본값 반환
person["hobby"] = "독서"            # 키가 없으면 추가, 있으면 수정
print(person.pop("job"))            # "학생", 키와 값을 삭제한 후 값 반환
```

키 존재 여부는 `if "age" in person:`으로 확인. 에러가 나면 Traceback의 **마지막 줄과 line 번호부터** 읽는다 (p.19).

### Java와 Python 비교 (p.20, 34)

| 구분 | Java | Python |
|---|---|---|
| 타입 시스템 | 정적 타입, 컴파일 시 결정 (`int n = 10;`) | **동적 타입**, 실행 시 결정 (`n = 10`) |
| 리스트 / 맵 | `int[] a = {1, 2, 3};` / `Map<String, Integer> m = new HashMap<>();` | `a = [1, 2, 3]` / `m = {"a": 1}` |
| 문장 종결·블록 | 세미콜론, 중괄호 `{}` | 줄바꿈, **들여쓰기** |
| 조건문 | `if (x > 0) { ... }` / `else if` | `if x > 0:` (콜론+들여쓰기) / `elif` |
| 반복 | `for (int i=0; i<n; i++)` / `for (int x : arr)` | `for i in range(n):` / `for x in arr:` |
| 함수 정의 | `int add(int a, int b){ return a+b; }` 반환 타입 명시 | `def add(a, b): return a + b` 불필요(자동 추론) |
| 불리언 | `boolean`, `true / false` | `bool`, `True / False` |

---

## 조건문, 반복문, 함수

### 조건문 (p.22-23, 31)

`if 조건:` → `elif 다른 조건:` → `else:` 순서로, 위에서부터 확인해 **처음으로 참인 분기 하나만** 실행. 블록은 공백 4칸 들여쓰기. 비교 연산자는 `==` `!=` `>` `<` `>=` `<=`.

> **주의** — 숫자와 문자열처럼 **종류가 다른 값은 같다고 보지 않는다** → `5 == "5"`는 **False** (p.23). API 응답에서 숫자가 문자열로 오면 형 변환 없이는 비교가 조용히 False가 된다.

### 거짓 값(Falsy) (p.24)

`0`, `""`, `[]`, `None`은 조건식에서 **거짓으로 평가**된다. 그래서 `scores = []`일 때 `if scores:`는 거짓 분기로 빠지고, 빈 리스트 검사는 `len(scores) == 0` 대신 **`if not scores`**가 관용 표현이다.

### 반복문 (p.25-27, 32)

`for`는 반복할 대상의 값을 변수에 하나씩 대입하며 반복. 합계 패턴: `total = 0` → `for score in scores: total = total + score` (p.32).

| 코드 | 결과 | 설명 |
|---|---|---|
| `range(5)` | 0, 1, 2, 3, 4 | 0부터 n-1까지 |
| `range(1, 5)` | 1, 2, 3, 4 | 끝 미포함 |
| `range(0, 10, 2)` | 0, 2, 4, 6, 8 | 2칸씩 증가 |
| `range(10, 0, -1)` | 10, 9, ..., 1 | 내림차순 |

`break`는 반복문 즉시 종료(`range(10)`에서 `i == 3`이면 break → 0, 1, 2), `continue`는 현재 반복만 건너뜀(`range(5)`에서 `i == 2`면 continue → 0, 1, 3, 4) (p.27).

```python
for i in range(3):
    print(i)
else:
    print("반복 완료")  # break가 실행되지 않았으므로 출력
```

> **주의** — **for-else**의 else는 "반복이 안 돌았을 때"가 아니라 **break 없이 반복이 끝났을 때** 실행된다 (p.27). 탐색 실패 처리(찾으면 break, 못 찾으면 else)에 쓰는 패턴.

### 함수와 스코프 (p.28-30, 33)

`def`로 정의, `return`으로 반환, 이름으로 여러 번 호출. `def average(numbers): return sum(numbers) / len(numbers)` — 내장 `sum()`·`len()` 조합이 기본 패턴 (p.33). 호출 스택(Call Stack): 호출된 함수의 실행 정보가 순서대로 쌓이고, 종료되면 최근 호출부터 제거 (p.29).

```python
global_var = 100  # 전역 변수, 함수 안과 밖에서 접근 가능

def my_func():
    local_var = 50       # 지역 변수, 함수 안에서만 접근 가능
    print(global_var)    # 100
    print(local_var)     # 50

my_func()
print(global_var)        # 100
print(local_var)         # NameError, 함수 밖에서 접근할 수 없음
```

| 변수 종류 | 정의 위치 | 접근 범위 | 생명 주기 |
|---|---|---|---|
| 전역 변수 | 함수 밖 | 함수 안과 밖 | 프로그램 종료까지 |
| 지역 변수 | 함수 안 | 정의한 함수 안 | **함수 종료까지** |

> **핵심** — 지역 변수는 함수가 종료되면 사라지고, 밖에서 접근하면 **NameError** (p.29-30). 밖에서 쓸 값은 `return`으로 내보내 변수에 받는다.

---

## API, HTTP, requests 기초

### API 개념 (p.36-37)

식당 비유: 손님=클라이언트, 메뉴판=**API 문서**, 주문=요청(request), 주방=서버, 음식=응답(response). 손님이 조리 과정을 몰라도 주문하듯, 클라이언트는 **서버 내부 처리를 몰라도** API로 요청을 보내고 응답을 받는다. URL은 요청할 자원의 위치를 나타내는 주소.

### HTTP 메서드와 상태 코드 (p.38-39)

| 메서드 | 용도 | | 코드 | 의미 |
|---|---|---|---|---|
| GET | 데이터 조회 ("메뉴판 보여 주세요") | | 200 | 요청 성공 |
| POST | 데이터 전송·생성 ("주문 접수해 주세요") | | 404 | 요청한 자원을 찾을 수 없음 |
| PUT / PATCH | 전체 / 일부 수정 | | 500 | 서버 내부 오류 |
| DELETE / OPTIONS | 삭제 / 가능한 메서드 확인 | | | |

### requests와 response 객체 (p.40-43)

`requests`는 HTTP 요청용 **외부 라이브러리** (`pip install requests`). `requests.get(URL)`은 응답을 Response 객체로 반환.

| 속성·메서드 | 자료형 | 의미 |
|---|---|---|
| `status_code` | int | HTTP 상태 코드 (200 등) |
| `text` | str | **문자열** 형태의 응답 본문 |
| `json()` | 메서드 | JSON 응답을 파싱해 **파이썬 객체**(리스트·딕셔너리)로 반환 |
| `headers` | CaseInsensitiveDict | 응답 헤더 |
| `elapsed` | timedelta | 응답에 걸린 시간 |
| `url` | str | 실제로 요청한 URL |

연습용 공개 API **JSONPlaceholder**(회원가입·API 키 불필요)로 테스트 (p.42-43):

```python
import requests

URL = "https://jsonplaceholder.typicode.com/users"
response = requests.get(URL, timeout=5)
print(response.status_code)   # 200, 요청 성공

if response.status_code == 200:
    data = response.json()    # JSON 응답을 파이썬 객체로 변환
    print(type(data))         # <class 'list'>
    print(len(data))          # 10, 사용자 수
```

> **주의** — 속성(`status_code`, `text`)은 점만, 메서드(`json()`)는 괄호까지 (p.41). 성공 여부는 `text`가 아니라 **`status_code`** 숫자로 판단하고(200=성공), 보통 `status_code == 200` 확인 뒤 `.json()`을 호출한다 (p.63).

### 예외 처리 — 원인별로 나눠 잡기 (p.44)

네트워크 요청은 응답 지연·연결 실패·HTTP 오류·JSON 변환 실패 예외가 날 수 있다. `except Exception` 하나로 뭉뚱그리지 말고 **원인별로 나누어** 처리.

```python
import json
import requests

try:
    response = requests.get(URL, timeout=5)
    response.raise_for_status()  # 400번대 또는 500번대이면 HTTPError 발생
    data = response.json()

except requests.exceptions.Timeout:
    print("5초 안에 응답을 받지 못함")
    data = []

except requests.exceptions.ConnectionError:
    print("서버에 연결할 수 없음")
    data = []

except requests.exceptions.HTTPError:
    print(
        f"HTTP 오류: {response.status_code} {response.reason}"
    )
    data = []

except json.JSONDecodeError:
    print("응답을 JSON으로 변환할 수 없음")
    data = []
```

> **핵심** — `raise_for_status()`가 4xx·5xx에서 HTTPError를 던져 주어야 "오류 응답인데 json() 파싱부터 하다 실패"하는 흐름을 걸러낼 수 있다. 각 except에서 `data = []` 기본값을 주면 이후 코드가 죽지 않는다.

---

## JSON 파싱과 LLM 연결

### JSON 구조 (p.46-47)

JSON은 프로그램 간 데이터 교환·저장용 **텍스트 기반 데이터 형식** — 파이썬과 웹(JS) 사이의 공통 형식.

```json
[
  {
    "id": 1,
    "name": "Leanne Graham",
    "email": "leanne@april.biz",
    "address": { "city": "Gwenborough", "zipcode": "92998" },
    "company": { "name": "Romaguera-Crona" }
  },
  { "id": 2, "name": "Ervin Howell", "email": "ervin@melissa.tv" }
]
```

- **배열(array)** → `response.json()` 하면 **리스트** / **객체(object)** → **딕셔너리**
- **중첩 객체** — `address`, `company`처럼 객체 안의 객체

### 중첩 데이터 접근 (p.48-50)

바깥쪽 구조부터 안쪽까지 순서대로: `data[0]["address"]["city"]` — 리스트에서 `[0]` → dict에서 `["address"]` → 그 안의 `["city"]`.

> **시험 포인트** — 파이썬 dict는 `.name`이 아니라 **`["name"]`**으로 접근한다 (p.49). JS식 `data[0].city`는 오답 (p.64-65 확인 문제의 오답 선택지).

API 응답의 **선택 항목**(있을 수도 없는 필드)은 `get()`으로: `user.get("phone")` → None, `user.get("phone", "N/A")` → `"N/A"` — 키가 없어도 죽지 않는다 (p.50).

### 필요한 값만 추출 (p.51)

응답에는 필요 없는 필드도 섞여 있으므로, 반복문으로 필요한 키만 뽑아 새 구조를 만든다.

```python
rows = []
for user in data:
    rows.append({
        "name": user["name"],
        "email": user["email"],
        "city": user["address"]["city"],
        "company": user["company"]["name"],
    })

print(rows[0])
# {'name': 'Leanne Graham', 'email': 'leanne@april.biz',
#  'city': 'Gwenborough', 'company': 'Romaguera-Crona'}
```

(슬라이드의 출력 주석에는 `' Leanne Graham'`처럼 이름 앞에 공백이 있는데, 실제 JSONPlaceholder 데이터에는 없다 — 슬라이드 오탈자로 보임.)

### LLM 호출과 컨텍스트 (p.52-53)

ChatGPT, Claude 같은 LLM은 **외부 AI 서버에서 실행**되고, API로 요청을 보내 응답을 받는다 — 이 자료의 `requests`(요청 전송)와 JSON(요청·응답 표현)이 그대로 LLM 연동의 재료.

- **컨텍스트** — 모델이 알지 못하는 최신·내부 정보를 질문과 함께 전달
- **RAG** — 질문과 관련된 자료를 **검색해** 컨텍스트로 전달
- **에이전트(Agent)** — 필요한 **도구를 사용해** 작업을 수행

```text
질문 + 찾은 자료 ──▶ context ──▶ LLM ──▶ 답변
```

### API 키 보안 (p.54-55)

API 키는 사용자를 식별·인증하는 비밀 정보. **노출되면 무단 사용으로 요금이 청구**될 수 있다.

- 키를 코드에 직접 쓰지 않고, GitHub 같은 공개 저장소에 올리지 않는다
- 환경 변수(`os.environ`)나 `.env` 파일로 관리 — `.env`는 `python-dotenv`로 읽고 **`.gitignore`에 추가**
- 공개 저장소에 올라갔다면 **즉시 폐기하고 새로 발급** — 파일을 삭제해도 **커밋 기록에는 남는다**
- 설정: macOS/Linux `export OPENAI_API_KEY="..."` / Windows `setx OPENAI_API_KEY "..."`

```python
import os

API_KEY = os.environ.get("OPENAI_API_KEY")  # 환경 변수가 없으면 None 반환

if not API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY 환경 변수가 설정되지 않음"
    )

headers = {
    "Authorization": f"Bearer {API_KEY}"
}
```

`Bearer`는 HTTP Authorization 헤더의 토큰 인증 표기. 환경 변수 부재는 None → `if not API_KEY`(Falsy 검사)로 잡는다.

### LLM API 요청·응답 (p.56-58)

요청 형식만 보여주는 의사코드(Pseudocode) — API 키로 POST 요청을 보내고, 응답 JSON 키에 순서대로 접근해 답변을 추출한다 (p.56-57 종합):

```python
headers = {
    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
}

body = {
    "model": "some-model",
    "messages": [
        {
            "role": "user",
            "content": prompt,
        }
    ],
    "temperature": 0.7,
    "max_tokens": 500,
}

response = requests.post(
    API_URL,
    headers=headers,
    json=body,
    timeout=30,
)

answer = response.json()["choices"][0]["message"]["content"]
```

| 요청 필드 | 자료형 | 의미 |
|---|---|---|
| `model` | str | 사용할 모델 |
| `messages` | list | **역할(role)과 내용(content)**으로 구성된 대화 목록 |
| `temperature` | float | 응답의 무작위성 — 낮을수록 일관, 높을수록 다양 |
| `max_tokens` | int | 출력할 수 있는 최대 토큰 수 |

응답 JSON 구조 (p.58):

```json
{
    "model": "some-model",
    "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75},
    "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "모델이 생성한 답변"}, "finish_reason": "stop"}
    ]
}
```

| 필드 경로 | 의미 | 자료형 |
|---|---|---|
| `choices[0]["message"]["content"]` | 응답 내용 | str |
| `usage["total_tokens"]` | 사용한 전체 토큰 수 | int |
| `choices[0]["finish_reason"]` | 응답 생성이 끝난 이유 | str |

> **핵심** — `choices`는 생성된 응답을 담은 **리스트**라 `choices[0]`이 첫 번째 응답이고, **비어 있지 않은지 확인한 후**(`if choices:`) 접근한다 (p.58). 결국 LLM 응답 파싱은 "리스트 인덱스 → dict 키" 중첩 접근 그 자체다.

---

## 정리 체크리스트

핵심 키워드 요약은 p.66-67 활동 정리 기준.

- [ ] `5 == "5"`가 False인 이유와 `int(3.14)`의 결과를 말할 수 있다
- [ ] 슬라이싱·range에서 끝 값이 포함되는지 답할 수 있다
- [ ] `append()`의 반환값과 `scores = scores.append(60)`이 잘못인 이유를 안다
- [ ] `sort()`/`sorted()`, `pop()`/`remove()`, `dict["키"]`/`get()`의 차이를 구분한다
- [ ] Falsy 값 4가지(`0`, `""`, `[]`, `None`)와 `if not scores` 관용구를 안다
- [ ] for-else의 else가 언제 실행되는지, 지역 변수를 밖에서 쓰면 무슨 에러인지 안다
- [ ] HTTP 메서드 6개와 상태 코드 200/404/500, `status_code`로 성공을 판단하는 이유를 안다
- [ ] `raise_for_status()`의 역할과 네트워크 예외 4종을 원인별 except로 쓸 수 있다
- [ ] `data[0]["address"]["city"]`처럼 중첩 JSON을 바깥→안 순서로 접근할 수 있다
- [ ] LLM 요청 body 4개 필드와 답변 추출 경로, API 키 관리 원칙(.env+.gitignore)을 안다

## 복습 문제

원본 확인 문제 3개(p.60-65) + 함정 포인트 보충.

**1.** (p.60-61) 다음 중 자료형이 str인 것은? ① `10` ② `3.14` ③ `"10"` ④ `True`

<details><summary>답</summary>

**③ `"10"`** — 따옴표로 감싸면 숫자처럼 보여도 문자열. `10`은 int, `3.14`는 float, `True`는 bool. `type("10")` → `<class 'str'>`.
</details>

**2.** (p.62-63) `requests.get()`의 응답이 성공했는지 확인할 때 보는 값은? ① `response.text` ② `response.status_code` ③ `response.json()` ④ `response.url`

<details><summary>답</summary>

**② `response.status_code`** — 성공 여부는 상태 코드 숫자로 판단(200=성공). `.text`와 `.json()`은 본문을 꺼내는 용도. 보통 `status_code == 200` 확인 뒤 `.json()` 호출.
</details>

**3.** (p.64-65) `[ { "name": "김싸피", "address": { "city": "Gwenborough" } } ]`에서 첫 번째 사용자의 도시를 꺼내는 코드는? ① `data["city"]` ② `data[0].city` ③ `data[0]["address"]["city"]` ④ `data["address"][0]["city"]`

<details><summary>답</summary>

**③** — 바깥이 list이므로 `[0]`으로 첫 항목 → dict이므로 `["address"]` → `["city"]`. 파이썬 dict는 `.키`가 아니라 `["키"]`로 접근하므로 ②는 오답.
</details>

**4.** `scores = [90, 85]; scores = scores.append(70)` 실행 후 `scores`의 값은?

<details><summary>답</summary>

**None.** `append()`는 리스트를 제자리에서 수정하고 None을 반환하므로 반환값을 다시 저장하면 리스트를 잃는다 (p.67). `scores.append(70)`만 호출하는 것이 맞다.
</details>

---

> **읽은 방식 메모** — 전체 68페이지를 1100px 렌더링 이미지로 직접 판독했고, 코드가 밀집된 p.44(예외 처리)·p.51(값 추출)·p.56-58(LLM 요청·응답)은 1700px로 재렌더링해 원문 대조를 마쳤다. OCR은 사용하지 않았다. 코드 블록과 표의 값은 슬라이드 원문 그대로이며, 예외적으로 p.56 의사코드에는 p.57의 `temperature`·`max_tokens` 필드를 합쳐 실었고, p.51 출력 주석의 이름 앞 공백은 슬라이드 오탈자로 판단해 바로잡았다(본문에 주석).
