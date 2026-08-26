# 파이썬 스코프와 global — LEGB, 대입이 정하는 소속, nonlocal까지

> 자기주도 학습 정리 · 정리일: 2026-08-26
> 블로그 발행본: https://it-study-2002.tistory.com/entry/파이썬-스코프와-global

파이썬을 좀 쓰다 보면 반드시 한 번은 만나는 장면이 있다. 함수 안에서 밖의 변수를 **읽는 것**은 아무 문제 없이 되는데, 거기에 **값을 넣으려는 순간** 갑자기 에러가 난다. 그것도 "없는 변수"라는 이유로. 분명 위에 선언해 뒀는데 말이다.

```python
count = 0

def add():
    count = count + 1     # UnboundLocalError: cannot access local variable 'count'

add()
```

읽기만 하는 코드로 바꾸면 멀쩡히 돈다. 한 줄에 읽기와 쓰기가 같이 있을 뿐인데 왜 갑자기 없는 변수가 되는가. 이 질문에 답하려면 **파이썬이 이름을 언제, 어떤 순서로 결정하는지**를 알아야 한다.

이 글은 그 규칙을 한 번에 정리한 것이다. 이름을 찾는 순서부터 시작해 `global`과 `nonlocal`, 가변 객체가 예외처럼 보이는 이유, 모듈 사이의 전역, 그리고 **전역을 안 쓸 수 없는 상황에서 안전하게 다루는 법**까지 다룬다.

## 📖 이 글에서 다루는 내용

1. LEGB — 이름을 찾는 순서
2. 대입 한 줄이 변수의 소속을 바꾼다
3. `UnboundLocalError` — 위 예제의 정체
4. `global` — 밖의 이름에 대입하겠다는 선언
5. 가변 객체는 `global` 없이도 바뀐다
6. `nonlocal` — 전역이 아니라 한 칸 위
7. 모듈 전역과 `import`
8. 스코프인 것과 아닌 것
9. 전역을 안 쓸 수 없을 때
10. 흔한 실수 여섯 가지
11. 핵심 요약

---

## 1. LEGB — 이름을 찾는 순서

파이썬이 `x`라는 이름을 만나면 네 군데를 **정해진 순서로** 뒤진다. 앞에서 찾으면 거기서 멈춘다.

> **[그림]** Local에서 시작해 Enclosing 함수, Global 모듈, Builtins 순서로 이름을 찾아 올라가고 어디에도 없으면 NameError가 발생하는 LEGB 탐색 순서

| 약자 | 이름 | 어디 |
|---|---|---|
| **L** | Local | 지금 실행 중인 함수 안 |
| **E** | Enclosing | 나를 감싸고 있는 바깥 함수 (중첩 함수일 때) |
| **G** | Global | 이 **모듈(.py 파일)** 의 최상단 |
| **B** | Built-in | `len`, `print`, `sum` 같은 내장 이름 |

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)        # local     ← L에서 찾고 멈춘다
    inner()
    print(x)            # enclosing ← inner의 x는 안 보인다
outer()
print(x)                # global
```

네 군데 어디에도 없으면 `NameError`가 난다.

> ⚠️ **Global은 "프로그램 전체"가 아니라 "이 파일"이다**
> 파이썬의 전역은 모듈 단위다. `a.py`의 최상단 변수는 `b.py`에서 그냥은 안 보인다. 다른 언어의 진짜 전역 변수를 떠올리면 7절에서 헷갈린다.

> 💡 **내장 이름을 가리면 조용히 망가진다**
> `list = [1, 2, 3]` 이라고 쓰는 순간, 그 모듈에서 `list()`는 더 이상 생성자가 아니다. `sum`, `max`, `min`, `id`, `type`, `dir`, `input`, `str` 이 자주 당한다. **B는 탐색의 마지막이라 앞의 무엇에든 가려진다.**

---

## 2. 대입 한 줄이 변수의 소속을 바꾼다

여기가 이 글의 핵심이다. 파이썬은 이름을 **실행하면서 찾는 게 아니라, 함수를 컴파일할 때 미리 분류한다.**

규칙은 딱 한 줄이다.

> **함수 본문 어딘가에 그 이름에 대한 대입이 있으면, 그 이름은 그 함수의 지역 변수다.** 대입이 함수의 몇 번째 줄에 있든 상관없다.

> **[그림]** 함수 본문에 대입이 하나라도 있으면 파이썬은 컴파일 시점에 그 이름을 지역 변수로 확정하고 함수 안 어디서든 지역으로 취급한다는 것을 보여주는 다이어그램

"대입"에는 우리가 잘 안 세는 것들도 들어간다.

| 형태 | 예 |
|---|---|
| 일반 대입 | `x = 1` |
| 복합 대입 | `x += 1`, `x *= 2` |
| 반복문 변수 | `for x in ...:` |
| `with ... as` | `with open(f) as x:` |
| `except ... as` | `except E as x:` |
| import | `import x`, `from m import x` |
| 함수·클래스 정의 | `def x(): ...`, `class x: ...` |
| 언패킹 | `a, x = 1, 2` |
| 바다코끼리 | `if (x := f()):` |

실제로 분류 결과를 눈으로 볼 수 있다.

```python
def f():
    print(y)      # 읽기만 한다
    z = 1         # 대입이 있다

print(f.__code__.co_varnames)    # ('z',)     ← z만 지역
print(f.__code__.co_names)       # ('print', 'y')  ← y는 지역이 아니다
```

`co_varnames`에 들어간 이름은 **함수 안 어디서 나오든 지역**으로 취급된다. 실행 순서와는 아무 관계가 없다.

---

## 3. `UnboundLocalError` — 위 예제의 정체

이제 맨 처음 코드를 다시 본다.

```python
count = 0

def add():
    count = count + 1
```

`count = ...` 라는 대입이 있으니 **`count`는 `add`의 지역 변수로 확정된다.** 그런데 오른쪽의 `count + 1`을 계산하려면 `count`를 읽어야 하고, 그 `count`는 이제 지역 변수인데 아직 아무 값도 안 들어갔다.

> **[그림]** 대입이 있어서 지역 변수로 확정되었지만 대입이 실행되기 전에 읽으려 해서 값이 없는 상태를 접근하는 UnboundLocalError 발생 순간

그래서 나는 에러가 이것이다.

```text
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

**`NameError`가 아니라 `UnboundLocalError`라는 점이 단서다.** "이름이 없다"가 아니라 "지역 변수인 건 아는데 값이 아직 없다"는 뜻이다. 이 에러를 보면 **밖에 있는 같은 이름을 실수로 건드리려 한 것**이라고 생각하면 거의 맞다.

같은 함정이 좀 더 얄궂게 나오는 경우도 있다.

```python
x = 10

def f():
    print(x)      # UnboundLocalError — 여기서 터진다
    x = 20        # 이 줄 때문에

f()
```

`print(x)`가 `x = 20`보다 **위에 있는데도** 터진다. 분류는 실행 전에 끝나 있기 때문이다.

> ⚠️ **잘 돌던 함수에 대입 한 줄을 추가했더니 다른 줄이 터진다**
> 이 에러가 나오는 가장 흔한 경로다. 읽기만 하던 함수에 나중에 `total = 0` 같은 줄을 넣는 순간, 그 함수 안의 **모든** `total`이 지역으로 바뀌면서 위쪽 코드가 같이 죽는다.

---

## 4. `global` — 밖의 이름에 대입하겠다는 선언

`global x`는 "이 함수 안에서 `x`는 지역이 아니라 모듈 전역을 가리킨다"고 컴파일러에게 알려주는 선언이다. **읽기 권한을 주는 게 아니라, 대입의 목적지를 바꾸는 것**이다.

> **[그림]** global 선언이 없으면 함수 안의 대입이 지역 변수를 새로 만들고 global 선언이 있으면 같은 대입이 모듈 전역 변수를 바꾼다는 비교

```python
count = 0

def add():
    global count
    count += 1        # 이제 모듈 전역 count 를 바꾼다

add(); add()
print(count)          # 2
```

알아 둘 성질이 몇 가지 있다.

- **읽기만 할 거면 `global`이 필요 없다.** LEGB가 알아서 G까지 올라간다. 붙여도 동작은 같지만 "여기서 값을 바꾸는구나"라는 잘못된 신호를 준다.
- **`global`은 함수 전체에 적용된다.** 함수 중간에 써도 첫 줄에 쓴 것과 같다. 관례상 맨 위에 모아 쓴다.
- **없던 전역도 만든다.** 함수 안에서 `global new_var` 뒤에 대입하면 모듈 전역에 새 이름이 생긴다.
- **모듈 최상단에서 쓴 `global`은 아무 일도 안 한다.** 거기가 이미 전역이다.

```python
def make():
    global brand_new
    brand_new = 42

make()
print(brand_new)      # 42 — 함수가 전역을 새로 만들었다
```

> 💡 **`globals()` 로 딕셔너리를 직접 만질 수도 있다**
> `globals()["x"] = 1` 은 동작한다. 하지만 이름이 문자열로 숨어서 코드 검색·리팩터링·타입 검사가 전부 무력해진다. 정말로 이름을 동적으로 만들어야 하는 상황이면 **전역이 아니라 딕셔너리를 하나 두는 게 맞다.**

---

## 5. 가변 객체는 `global` 없이도 바뀐다

여기서 규칙이 깨지는 것처럼 보이는 장면이 나온다.

```python
nums = [1, 2, 3]

def f():
    nums.append(4)    # global 없이도 된다

f()
print(nums)           # [1, 2, 3, 4]
```

`global`을 안 썼는데 전역이 바뀌었다. 규칙이 틀린 걸까? 아니다. **`nums.append(4)`에는 `nums`에 대한 대입이 없다.** 이름을 읽어서 그 객체를 찾아간 뒤, 객체 안을 고친 것뿐이다.

> **[그림]** 이름을 다른 객체에 다시 묶는 재바인딩은 global이 필요하지만 이름이 가리키는 객체의 내용을 고치는 제자리 수정은 읽기만 하므로 global이 필요 없다는 비교

두 가지를 구분하면 전부 설명된다.

| | 하는 일 | 예 | `global` 필요? |
|---|---|---|---|
| **재바인딩** | 이름을 **다른 객체**에 다시 묶는다 | `nums = []`, `nums += [4]` | 필요하다 |
| **제자리 수정** | 이름이 가리키는 **객체 내용**을 고친다 | `nums.append(4)`, `nums[0] = 9`, `d["k"] = 1` | 필요 없다 |

```python
nums = [1, 2, 3]

def rebind():
    nums = []          # 지역 변수 nums 를 새로 만들 뿐
def mutate():
    nums.clear()       # 전역이 가리키는 리스트를 비운다

rebind(); print(nums)  # [1, 2, 3] — 안 바뀐다
mutate(); print(nums)  # []        — 바뀐다
```

### `+=` 가 특히 헷갈린다

리스트의 `+=`는 내부적으로 `__iadd__`를 불러 **제자리 확장**을 하지만, 문법상으로는 **대입**이다. 그래서 함수 안에서 쓰면 `nums`가 지역으로 분류되어 `UnboundLocalError`가 난다.

```python
nums = [1, 2, 3]

def f():
    nums += [4]        # UnboundLocalError — 대입이라서 지역으로 분류된다

def g():
    nums.extend([4])   # 정상 — 대입이 없다
```

**"제자리 수정이면 되는 줄 알았는데 `+=`만 안 되는" 현상의 정체가 이것이다.**

> 💡 **가변 기본 인자도 같은 뿌리다**
> `def f(acc=[])` 의 `[]`는 함수를 정의할 때 **한 번만** 만들어져서 호출 사이에 살아남는다. 호출마다 새 리스트를 원하면 `def f(acc=None)` 으로 두고 안에서 `if acc is None: acc = []` 로 만든다. 전역은 아니지만 "이름과 객체는 다르다"는 같은 이야기다.

---

## 6. `nonlocal` — 전역이 아니라 한 칸 위

중첩 함수에서 **바깥 함수의 지역 변수**를 바꾸고 싶을 때가 있다. 여기에 `global`을 쓰면 모듈 전역으로 튀어버린다. 그럴 때 쓰는 것이 `nonlocal`이다.

> **[그림]** global은 모듈 최상단으로 곧장 올라가고 nonlocal은 나를 감싸는 바깥 함수의 지역 변수를 가리킨다는 차이

```python
def counter():
    n = 0
    def tick():
        nonlocal n        # counter 의 n 을 가리킨다
        n += 1
        return n
    return tick

c = counter()
print(c(), c(), c())      # 1 2 3
```

`counter()`는 이미 끝났는데 `n`이 살아 있다. 안쪽 함수가 바깥 함수의 변수를 붙잡고 있는 이 구조를 **클로저**라고 부른다.

| | 대상 | 없는 이름이면 |
|---|---|---|
| `global x` | 모듈 최상단 | 대입하면 **새로 만든다** |
| `nonlocal x` | 나를 감싸는 가장 가까운 바깥 함수 | **`SyntaxError`** — 새로 만들지 않는다 |

`nonlocal`이 없는 이름에 대해 문법 오류를 내는 것은 의도된 설계다. 오타를 컴파일 시점에 잡아 준다.

> ⚠️ **반복문 안에서 함수를 만들 때 흔히 걸린다**
> `[lambda: i for i in range(3)]` 로 만든 함수 세 개를 나중에 부르면 전부 `2`를 돌려준다. 클로저는 **값이 아니라 변수를 붙잡기** 때문이다. 그 시점의 값을 굳히려면 `lambda i=i: i` 처럼 기본 인자로 받아 둔다.

---

## 7. 모듈 전역과 `import`

전역이 모듈 단위라는 말이 실제로 무슨 뜻인지는 `import`에서 드러난다. **`import` 방식에 따라 다른 모듈의 전역이 바뀌는 게 보이기도 하고 안 보이기도 한다.**

> **[그림]** 모듈 자체를 import하면 접근할 때마다 모듈의 현재 값을 읽지만 from import로 값을 가져오면 그 시점의 값이 내 모듈 이름에 복사되어 원본이 바뀌어도 따라오지 않는다는 비교

```python
# config.py
mode = "dev"
def set_mode(m):
    global mode
    mode = m
```

```python
# a.py — 모듈째로 가져온다
import config
config.set_mode("prod")
print(config.mode)        # prod  ← 매번 config 의 현재 값을 읽는다
```

```python
# b.py — 값을 가져온다
from config import mode, set_mode
set_mode("prod")
print(mode)               # dev   ← 내 모듈의 mode 는 그대로다
```

`from config import mode`는 **그 순간의 값을 내 모듈 전역에 복사해 이름을 하나 새로 만든다.** 원본이 나중에 바뀌어도 따라오지 않는다.

| 방식 | 나중에 원본이 바뀌면 |
|---|---|
| `import config` 뒤 `config.mode` | 따라온다 |
| `from config import mode` | 따라오지 않는다 |

> ✅ **바뀌는 값은 모듈째로 가져온다**
> 설정값, 카운터, 캐시처럼 실행 중에 바뀌는 것은 `import config` 로 가져와 `config.mode` 로 쓴다. 상수나 함수, 클래스처럼 안 바뀌는 것만 `from ... import` 로 꺼내 쓰면 헷갈릴 일이 없다.

---

## 8. 스코프인 것과 아닌 것

다른 언어를 먼저 배웠으면 여기서 한 번 미끄러진다. **파이썬에서 `if`, `for`, `while`, `try` 블록은 스코프를 만들지 않는다.**

> **[그림]** if와 for 같은 블록은 스코프를 만들지 않아 변수가 밖에서도 보이지만 함수와 컴프리헨션은 자체 스코프를 만들어 변수가 밖으로 나오지 않는다는 비교

```python
if True:
    inside = 1
print(inside)         # 1 — 블록 밖에서도 보인다

for i in range(3):
    pass
print(i)              # 2 — 반복이 끝나도 남아 있다
```

스코프를 만드는 것은 **함수, 클래스, 모듈, 그리고 컴프리헨션**이다.

### 컴프리헨션은 스코프다

```python
i = "원래 값"
squares = [i * i for i in range(3)]
print(i)              # 원래 값 — 컴프리헨션의 i 는 밖으로 안 샌다
```

파이썬 3부터 컴프리헨션은 자체 스코프를 갖는다. **일반 `for` 문과 정반대**라서 헷갈리기 딱 좋다.

### 클래스 본문은 스코프지만 좀 특이하다

```python
class C:
    n = 3
    def m(self):
        return n      # NameError — 클래스 본문은 LEGB의 E가 아니다
```

메서드 안에서 클래스 변수를 쓰려면 `self.n` 또는 `C.n` 이라고 명시해야 한다. **클래스 본문 스코프는 메서드에게 상속되지 않는다.**

> ⚠️ **클래스 본문 안의 컴프리헨션에서 클래스 변수가 안 보인다**
> ```python
> class C:
>     vals = [1, 2, 3]
>     doubled = [v * 2 for v in vals]        # 된다 (첫 iterable 만 예외)
>     bad = [v * len(vals) for v in vals]    # NameError: name 'vals' is not defined
> ```
> 컴프리헨션이 별도 스코프인데 클래스 본문은 감싸는 스코프로 안 쳐 주기 때문이다. 첫 번째 `for`의 순회 대상만 바깥에서 평가되어 예외적으로 통한다. 알고 나면 `for v in vals` 는 되는데 안쪽에서 `vals` 를 또 쓰면 터지는 이유가 설명된다.

---

## 9. 전역을 안 쓸 수 없을 때

"전역 쓰지 마라"는 조언은 대체로 맞다. 하지만 **구조상 전역이 강제되는 자리**가 있다. 대표적인 게 채점 시스템이 정해 준 함수 몇 개만 구현하는 형식이다.

```python
def init(N, board): ...
def add(x, y): ...
def query(k): ...
```

세 함수가 상태를 공유해야 하는데 서로 인자를 주고받을 수 없다. 클래스로 감싸도 결국 그 인스턴스를 담을 전역이 하나 필요하다. 이럴 때는 **없애는 게 아니라 안전하게 쓰는 쪽**으로 방향을 잡는다.

> **[그림]** 전역 상태를 딕셔너리 하나나 클래스 인스턴스로 모으고 초기화 함수에서 전부 다시 세우면 초기화 누락과 선언 누락이 구조적으로 막힌다는 세 가지 패턴

### 규칙 하나 — 초기화 함수에서 전부 다시 세운다

가장 자주 나는 사고가 **이전 실행의 상태가 남아 있는 것**이다. 함수가 여러 번 호출되는 형식이면 특히 그렇다.

```python
def init(N):
    global board, count, cache
    board = [[0] * N for _ in range(N)]
    count = 0
    cache = {}            # 여기서 하나라도 빠지면 이전 값이 남는다
```

**전역 목록과 초기화 목록이 글자 그대로 일치하는지** 눈으로 맞춰 보는 습관이 제일 싸게 먹힌다.

### 규칙 둘 — 리스트를 늘릴 때는 짝을 맞춘다

같은 대상에 대한 정보를 여러 리스트에 나눠 담으면, 하나를 늘릴 때 나머지를 빠뜨리기 쉽다.

```python
def add_item(v):
    global n
    items.append(v)
    ready.append(0)       # 이 줄을 빼먹으면 나중에 IndexError
    target.append(-1)     # 이 줄도
    n += 1                # append 뒤에 와야 인덱스가 맞는다
```

리스트가 세 개를 넘어가면 **딕셔너리 하나에 모으거나 작은 클래스로 묶는 편**이 낫다. 늘리는 자리가 한 곳이 되면 빠뜨릴 수가 없다.

```python
class Item:
    __slots__ = ("value", "ready", "target")
    def __init__(self, v):
        self.value, self.ready, self.target = v, 0, -1

def add_item(v):
    items.append(Item(v))     # 늘리는 곳이 한 군데
```

### 규칙 셋 — 상태를 한 곳에 모은다

전역 이름이 열 개를 넘어가면 `global` 선언 줄이 함수마다 길어지고, 어느 함수가 무엇을 바꾸는지 추적이 안 된다. **딕셔너리 하나에 모으면 `global` 선언 자체가 필요 없어진다.** 5절에서 본 대로 딕셔너리 내용을 고치는 건 제자리 수정이라 선언이 필요 없기 때문이다.

```python
S = {}                    # 전역은 이 하나뿐

def init(N):
    S.clear()             # 재바인딩이 아니라 제자리 비우기
    S.update(board=[[0] * N for _ in range(N)], count=0, cache={})

def add(x, y):
    S["board"][x][y] = 1  # global 선언이 필요 없다
    S["count"] += 1
```

`S = {}` 로 다시 대입하면 `global`이 필요해지므로 **`clear()` + `update()`** 로 비우는 게 요령이다.

> ✅ **판단 기준**
> 전역이 두세 개고 초기화가 단순하면 그냥 `global`을 쓴다. **열 개를 넘거나, 초기화 함수가 여러 번 불리거나, 리스트끼리 인덱스를 맞춰야 하면** 딕셔너리나 클래스로 모은다. 이때 얻는 건 코드 미학이 아니라 **초기화 누락과 인덱스 어긋남을 구조적으로 못 하게 막는 것**이다.

---

## 10. 흔한 실수 여섯 가지

**하나. 읽기만 하는데 `global`을 붙인다.** 동작은 같지만 읽는 사람에게 "여기서 값을 바꾼다"는 잘못된 신호를 준다. 대입이 있을 때만 붙인다.

**둘. `global`을 쓰고도 안 바뀐다.** 대개 **다른 모듈에서 `from m import x` 로 가져다 본 경우**다. 7절 그대로다. 값을 복사해 온 이름은 원본이 바뀌어도 안 따라온다.

**셋. `nonlocal` 자리에 `global`을 쓴다.** 중첩 함수에서 바깥 함수 변수를 바꾸려다 모듈 전역을 만들어 버린다. 원래 고치려던 값은 그대로 남아 있어서 원인을 찾기 어렵다.

**넷. 반복문 변수를 나중에 그대로 쓴다.** `for i in ...` 이 끝나도 `i`가 남아 있어서, 다른 곳에서 쓰던 `i`를 덮어쓴다. 반복이 한 번도 안 돌았으면 `i` 자체가 없어서 `NameError`가 난다.

**다섯. 내장 이름을 가린다.** `sum = 0` 을 써 놓고 아래에서 `sum(nums)` 를 부르면 `TypeError: 'int' object is not callable` 이 난다. 에러 메시지가 원인을 안 알려주는 대표적인 경우다.

**여섯. 테스트 케이스 사이에 전역을 안 지운다.** 여러 케이스를 도는 문제에서 앞 케이스의 값이 남아 두 번째부터 답이 어긋난다. **첫 케이스만 맞고 나머지가 다 틀리면 여기부터 본다.**

---

## ✅ 핵심 요약

| 주제 | 꼭 기억할 것 |
|---|---|
| **LEGB** | Local → Enclosing → Global → Built-in 순으로 찾고 먼저 찾으면 멈춘다 |
| **Global의 범위** | 프로그램 전체가 아니라 **모듈(.py 파일) 하나** |
| **분류 시점** | 실행 중이 아니라 **컴파일할 때** 정해진다. 대입이 몇 번째 줄이든 상관없다 |
| **핵심 규칙** | 함수 안에 그 이름에 대한 **대입이 하나라도 있으면 지역 변수** |
| **"대입"의 범위** | `=` 말고도 `+=`, `for x in`, `with as`, `except as`, `import`, `def`, `class` |
| **`UnboundLocalError`** | "이름이 없다"가 아니라 "지역인데 값이 아직 없다". 밖의 변수를 건드리려 한 신호 |
| **`global`** | 읽기 권한이 아니라 **대입의 목적지**를 바꾸는 선언. 읽기만 하면 필요 없다 |
| **재바인딩 vs 제자리 수정** | `nums = []` 는 `global` 필요, `nums.append()` 는 불필요 |
| **`+=` 의 함정** | 리스트라도 문법상 대입이라 지역으로 분류된다. `extend()` 는 안 그렇다 |
| **`nonlocal`** | 바깥 **함수**의 변수. 없는 이름이면 `SyntaxError`로 즉시 잡아 준다 |
| **클로저** | 값이 아니라 **변수**를 붙잡는다. 값을 굳히려면 기본 인자로 받는다 |
| **`from m import x`** | 그 순간의 값을 복사한다. 바뀌는 값은 `import m` 뒤 `m.x` 로 쓴다 |
| **블록은 스코프가 아니다** | `if`, `for`, `while`, `try` 안의 변수는 밖에서도 보인다 |
| **컴프리헨션은 스코프다** | 파이썬 3부터. 일반 `for` 문과 정반대라 헷갈린다 |
| **클래스 본문** | 메서드에서 안 보인다. `self.n` 또는 `C.n` 으로 명시한다 |
| **전역이 강제될 때** | 초기화 함수에서 **전역 목록 전부**를 다시 세운다. 하나라도 빠지면 이전 값이 남는다 |
| **상태 모으기** | 전역이 열 개를 넘으면 딕셔너리나 클래스로. `S.clear()` + `S.update()` 로 비운다 |

## 🔗 참고 자료

- [파이썬 공식 문서 — 이름과 바인딩 (Execution model)](https://docs.python.org/ko/3/reference/executionmodel.html#naming-and-binding)
- [파이썬 공식 문서 — global 문](https://docs.python.org/ko/3/reference/simple_stmts.html#the-global-statement)
- [파이썬 공식 문서 — nonlocal 문](https://docs.python.org/ko/3/reference/simple_stmts.html#the-nonlocal-statement)
- [파이썬 공식 FAQ — 지역 변수 규칙](https://docs.python.org/ko/3/faq/programming.html#what-are-the-rules-for-local-and-global-variables-in-python)
