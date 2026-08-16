# Cookie & Session

> 출처: `16기_데이터트랙_0803_Django_Authentication.pdf` (총 103페이지) · 정리일: 2026-08-03
> 시리즈: **01 Cookie & Session** · [02 Authentication with DRF](django-authentication-02-authentication-with-drf.md)
> 페이지 표기는 PDF 물리 페이지 기준. 슬라이드 인쇄 번호와 동일하다.

## 한눈에 보기

- HTTP는 왜 "상태가 없는" 프로토콜이고, 그것이 왜 문제가 되는가
- 쿠키는 무엇을 저장하며, 언제 서버로 다시 전송되는가
- 세션은 쿠키와 무엇이 다른가 — 실제 데이터는 어디에 저장되는가
- Django에서 세션은 어떤 테이블의 어떤 컬럼에 저장되는가
- Session cookie와 Persistent cookie는 각각 언제 삭제되는가

## 목차

1. [HTTP와 상태 유지 문제](#http와-상태-유지-문제) (p.4-9)
2. [쿠키](#쿠키) (p.10-22)
3. [세션](#세션) (p.23-32)
4. [쿠키 Lifetime과 Django 세션](#쿠키-lifetime과-django-세션) (p.33-35)

---

## HTTP와 상태 유지 문제

### HTTP란 (p.6-7)

**HTML 문서와 같은 리소스들을 가져올 수 있도록 해주는 규약**이다. 웹(WWW)에서 이루어지는 모든 데이터 교환의 기초가 된다.

여기서 오해하기 쉬운 지점이 하나 있다. 브라우저에 페이지가 떠 있다고 해서 서버와 계속 연결되어 있는 것이 아니다.

```text
Client  ──── 요청 ────▶  Server
        ◀─── 응답 ────
                          (연결 끊김)

우리가 서버로부터 받은 페이지를 둘러볼 때
우리는 서버와 서로 연결되어 있는 상태가 아니다.
```

### HTTP의 두 가지 특징 (p.8)

| 특징 | 설명 |
|---|---|
| **비연결 지향 (connectionless)** | 서버는 요청에 대한 응답을 보낸 후 연결을 끊음 |
| **무상태 (stateless)** | 연결을 끊는 순간 클라이언트와 서버 간의 통신이 끝나며 상태 정보가 유지되지 않음 |

> **시험 포인트** — 두 용어의 영문 철자와 정의를 그대로 묻는 문제가 나오기 쉽다. `connectionless`는 "연결을 끊는다", `stateless`는 "상태를 기억하지 않는다"로 구분해 외운다.

### 상태가 없다는 것의 결과 (p.9)

- 장바구니에 담은 상품을 유지할 수 없음
- 로그인 상태를 유지할 수 없음

→ **상태를 유지하기 위한 기술이 필요**하다. 이 필요에서 쿠키와 세션이 나온다.

---

## 쿠키

### 쿠키란 (p.10-12)

**서버가 사용자의 웹 브라우저에 전송하는 작은 데이터 조각**이다.

→ 클라이언트 측에서 저장되는 작은 데이터 파일이며, **사용자 인증, 추적, 상태 유지** 등에 사용되는 데이터 저장 방식이다.

### 쿠키의 동작 3단계 (p.13-15)

```text
1. The browser requests a web page
   Web browser ──────────────────────────▶ Web server

2. The server sends the page and the cookie 🍪
   Web browser ◀────────────────────────── Web server

3. The browser requests another page from the same server 🍪
   Web browser ──────────────────────────▶ Web server
   (저장해 두었던 쿠키를 함께 전송)
```

서버로부터 쿠키를 받고, 같은 서버의 다른 페이지로 재요청할 때마다 저장해 놓았던 쿠키를 함께 전송한다.

### 브라우저가 실제로 하는 일 (p.16)

1. 브라우저(클라이언트)는 쿠키를 **KEY-VALUE의 데이터 형식**으로 저장한다
2. 이렇게 쿠키를 저장해 놓았다가, **동일한 서버에 재요청 시** 저장된 쿠키를 함께 전송한다

→ 쿠키는 **두 요청이 동일한 브라우저에서 들어왔는지 아닌지를 판단할 때** 주로 사용된다.

- 이를 이용해 사용자의 로그인 상태를 유지할 수 있음
- 상태가 없는(stateless) HTTP 프로토콜에서 **상태 정보를 기억시켜 주기 때문**

### 장바구니 예시로 보는 쿠키 (p.17-21)

쇼핑몰에서 장바구니에 상품을 담은 뒤 개발자 도구로 추적하는 실습이다. 흐름만 잡아두면 된다.

| 단계 | 확인 위치 | 보이는 것 |
|---|---|---|
| 상품 담기 | 화면 | 장바구니에 상품이 추가됨 |
| 서버 응답 확인 | Network 탭 → 요청 → Headers | **`Set-Cookie`** 응답 헤더 |
| 쿠키 데이터 확인 | Network 탭 → Cookies | Name / Value 쌍 목록 |
| 재요청 확인 | Network 탭 → Request Headers | **`Cookie:`** 요청 헤더에 값이 실려 나감 |
| 쿠키 삭제 | Application 탭 → Cookies → 우클릭 Clear | 새로고침하면 **장바구니가 빔** |

> **핵심** — `Set-Cookie`는 **서버 → 클라이언트** 방향의 응답 헤더로, "이 쿠키를 저장하라"는 지시다. 반대로 `Cookie`는 **클라이언트 → 서버** 방향의 요청 헤더다. 방향이 반대인 두 헤더의 이름이 다르다는 점을 헷갈리지 않는다.

### 쿠키 사용 목적 (p.22)

1. **세션 관리 (Session management)**
   - 로그인, 아이디 자동완성, 공지 하루 안 보기, 팝업 체크, 장바구니 등의 정보 관리
2. **개인화 (Personalization)**
   - 사용자 선호, 테마 등의 설정
3. **트래킹 (Tracking)**
   - 사용자 행동을 기록 및 분석

---

## 세션

### 세션이란 (p.23-24)

**서버 측에서 생성되어 클라이언트와 서버 간의 상태를 유지하고, 상태 정보를 저장하는 데이터 저장 방식**이다.

→ 쿠키에 세션 데이터를 저장하여 매 요청 시마다 세션 데이터를 함께 보낸다.

> **쿠키 vs 세션, 한 문장 구분** — 쿠키는 **클라이언트**에 저장되는 데이터 조각이고, 세션은 **서버**에 저장되는 데이터다. 다만 그 세션에 접근할 열쇠(session id)는 쿠키에 담겨 오간다. 즉 **세션은 쿠키를 이용해 동작한다.**

### 세션 작동 원리 6단계 (p.25)

1. 클라이언트가 로그인을 하면 서버가 **session 데이터를 생성 후 저장**
2. 생성된 session 데이터에 인증할 수 있는 **session id를 발급**
3. 발급한 session id를 클라이언트에게 응답
4. 클라이언트는 응답받은 session id를 **쿠키에 저장**
5. 클라이언트가 다시 동일한 서버에 접속하면 요청과 함께 쿠키(session id가 저장된)를 서버에 전달
6. 쿠키는 요청 때마다 서버에 함께 전송되므로, 서버에서 session id를 확인해 **로그인되어 있다는 것을 알도록 함**

정리하면 이렇다 (p.26).

```text
[서버]  세션 데이터 생성 → 저장
        └─ 이 데이터에 접근할 수 있는 세션 ID 생성
                    │
                    ▼  ID 전달
[클라이언트]  쿠키에 이 ID를 저장
```

### Django 세션 생성 및 반환 예시 (p.27-30)

**① URL 연결과 커스텀 User 모델** (p.27)

```python
# my_api/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
]
```

```python
# accounts/urls.py
urlpatterns = [
    path("login/", views.login),
]
```

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser

# 장고 내장 User 모델을 상속받아 커스텀 유저 모델을 만듦
class User(AbstractUser):
    pass
```

**② 로그인 view** (p.28)

```python
# accounts/views.py
from django.contrib.auth.forms import AuthenticationForm  # 장고 내장 로그인 폼
from django.contrib.auth import login as auth_login       # 장고 내장 로그인 함수

def login(request):
    form = AuthenticationForm(request, request.POST)  # 사용자가 입력한 데이터를 폼에 넣음
    if form.is_valid():  # 유효성 검사
        user = form.get_user()  # form에서 user 객체를 가져옴
        auth_login(request, user)  # 로그인 함수 실행
        session_id = request.session.session_key  # 세션키를 가져옴
        response_data = {
            'message': 'Login successful',
            'session_id': session_id
        }
        return Response(response_data, status=status.HTTP_200_OK)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
```

> **눈여겨볼 곳** — `request.session.session_key`가 세션 ID를 꺼내는 지점이다. `auth_login()`이 실행되기 **전에는 세션키가 아직 없다.** 순서가 바뀌면 `None`이 나온다.

**③ 요청과 응답** (p.29)

Postman으로 `POST http://127.0.0.1:8000/accounts/login/` 요청을 보내면서 body에 `username`, `password`를 담으면 다음과 같은 응답이 온다.

```json
{
    "message": "Login successful",
    "session_id": "9lwy0uf9ww215beqgvuzy5bathbloez6"
}
```

**④ DB에 저장된 세션 확인** (p.30)

응답으로 받은 session_id와 동일한 값이 `django_session` 테이블에 들어 있다.

| 컬럼 | 타입 | 내용 |
|---|---|---|
| `session_key` | `varchar(40)` | 세션 ID. 클라이언트 쿠키에 저장되는 값 |
| `session_data` | `TEXT` | 인코딩된 세션 데이터 본문 |
| `expire_date` | `datetime` | 만료 시각 |

### 이후의 흐름과 목적 (p.31-32)

이후 클라이언트가 같은 서버에 재요청할 때마다 저장해 두었던 쿠키도 요청과 함께 전송된다. 예를 들어 로그인 상태 유지를 위해, **로그인되어 있다는 사실을 입증하는 데이터를 매 요청마다 계속해서 보내는 것**이다.

> **쿠키와 세션의 목적** — 서버와 클라이언트 간의 **'상태'를 유지**하는 것.

---

## 쿠키 Lifetime과 Django 세션

### 쿠키 종류별 Lifetime (p.33-34)

| 종류 | 삭제 시점 |
|---|---|
| **Session cookie** | 현재 세션(current session)이 종료되면 삭제됨. **브라우저 종료와 함께** 세션이 삭제됨 |
| **Persistent cookies** | **`Expires`** 속성에 지정된 날짜 혹은 **`Max-Age`** 속성에 지정된 기간이 지나면 삭제됨 |

> **시험 포인트** — 두 속성 이름(`Expires` / `Max-Age`)을 묻는 문제가 잘 나온다. `Expires`는 **절대 시각**(날짜), `Max-Age`는 **상대 기간**(초)이라는 차이도 함께 기억한다.

### 세션 in Django (p.35)

- Django는 **`database-backed sessions`** 저장 방식을 기본값으로 사용한다
- session 정보는 **DB의 `django_session` 테이블**에 저장된다
- Django는 요청 안에 있는 session id를 포함하는 쿠키를 사용해서, 각각의 브라우저와 사이트가 연결된 session 데이터를 알아낸다

→ Django는 우리가 session 메커니즘(복잡한 동작원리)에 대부분을 생각하지 않게끔 많은 도움을 준다.

---

## 정리 체크리스트

- [ ] HTTP의 두 특징 `connectionless`와 `stateless`를 영문 용어와 함께 설명할 수 있다
- [ ] 상태가 없어서 생기는 구체적 문제 두 가지를 말할 수 있다
- [ ] 쿠키의 정의와 저장 형식(KEY-VALUE)을 설명할 수 있다
- [ ] 쿠키 동작 3단계를 순서대로 말할 수 있다
- [ ] `Set-Cookie`와 `Cookie` 헤더의 방향 차이를 구분할 수 있다
- [ ] 쿠키 사용 목적 3가지를 영문 용어와 함께 나열할 수 있다
- [ ] 쿠키와 세션의 저장 위치 차이를 한 문장으로 말할 수 있다
- [ ] 세션 작동 원리 6단계를 순서대로 설명할 수 있다
- [ ] `django_session` 테이블의 세 컬럼과 타입을 말할 수 있다
- [ ] Session cookie와 Persistent cookies의 삭제 시점 차이를 말할 수 있다

## 복습 문제

**1.** HTTP의 두 가지 특징을 영문 용어와 함께 쓰고, 각각을 한 줄로 설명하시오.

<details>
<summary>답</summary>

- **비연결 지향(connectionless)** — 서버는 요청에 대한 응답을 보낸 후 연결을 끊는다.
- **무상태(stateless)** — 연결을 끊는 순간 클라이언트와 서버 간의 통신이 끝나며 상태 정보가 유지되지 않는다.

</details>

**2.** 쿠키는 브라우저에 어떤 데이터 형식으로 저장되는가?

<details>
<summary>답</summary>

**KEY-VALUE** 형식으로 저장된다.

</details>

**3.** 서버가 클라이언트에게 "이 쿠키를 저장하라"고 지시할 때 사용하는 HTTP 헤더 이름은?

<details>
<summary>답</summary>

**`Set-Cookie`** (응답 헤더). 반대로 클라이언트가 서버로 보낼 때는 **`Cookie`** 요청 헤더를 쓴다.

</details>

**4.** 쿠키의 사용 목적 3가지를 영문 용어와 함께 쓰시오.

<details>
<summary>답</summary>

1. 세션 관리 (Session management)
2. 개인화 (Personalization)
3. 트래킹 (Tracking)

</details>

**5.** 세션 작동 원리에서, 서버가 생성한 세션 데이터에 접근하기 위해 발급하는 것은 무엇이며 클라이언트는 그것을 어디에 저장하는가?

<details>
<summary>답</summary>

**session id**를 발급하고, 클라이언트는 이를 **쿠키**에 저장한다. 이후 매 요청마다 쿠키가 함께 전송되므로 서버가 session id로 로그인 상태를 확인할 수 있다.

</details>

**6.** Django에서 세션 정보가 저장되는 테이블 이름과 세 개의 컬럼을 타입까지 쓰시오.

<details>
<summary>답</summary>

테이블: **`django_session`**

| 컬럼 | 타입 |
|---|---|
| `session_key` | `varchar(40)` |
| `session_data` | `TEXT` |
| `expire_date` | `datetime` |

</details>

**7.** Django view에서 현재 요청의 세션 키를 가져오는 코드를 쓰시오.

<details>
<summary>답</summary>

```python
session_id = request.session.session_key
```

단, `auth_login(request, user)`가 실행된 **이후**여야 값이 존재한다.

</details>

**8.** Session cookie와 Persistent cookies의 삭제 시점을 각각 설명하시오.

<details>
<summary>답</summary>

- **Session cookie** — 현재 세션(current session)이 종료되면, 즉 브라우저 종료와 함께 삭제된다.
- **Persistent cookies** — `Expires` 속성에 지정된 날짜 혹은 `Max-Age` 속성에 지정된 기간이 지나면 삭제된다.

</details>

**9.** Django가 기본값으로 사용하는 세션 저장 방식의 이름은?

<details>
<summary>답</summary>

**`database-backed sessions`**

</details>

---

> **읽은 방식 메모** — 이 노트의 코드 블록과 DB 테이블 구조(p.27, p.28, p.30)는 원본 슬라이드를 2000px 이상으로 재렌더링해 육안 대조를 마쳤다. 한국어 설명문 중 p.16, p.34, p.35는 OCR 결과를 문맥으로 복원한 것이므로, 조사·어미 수준의 미세한 표현 차이가 있을 수 있다.
