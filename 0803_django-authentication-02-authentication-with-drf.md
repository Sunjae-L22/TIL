# Authentication with DRF

> 출처: `16기_데이터트랙_0803_Django_Authentication.pdf` (총 103페이지) · 정리일: 2026-08-03
> 시리즈: [01 Cookie & Session](0803_django-authentication-01-cookie-session.md) · **02 Authentication with DRF**
> 페이지 표기는 PDF 물리 페이지 기준.

## 한눈에 보기

- 인증(Authentication)과 권한(Permissions)은 무엇이 다르고 어느 쪽이 먼저 실행되는가
- 401과 403은 어떤 상황에서 각각 응답되는가
- 세션 인증 대신 토큰 인증을 쓰는 이유는 무엇인가
- DRF에서 인증·권한을 전역과 View 단위로 설정하는 두 가지 방법
- TokenAuthentication을 적용하는 4단계와, 토큰이 자동 생성되는 원리(Signals)
- 발급받은 토큰을 요청에 실어 보내는 정확한 헤더 형식

## 목차

1. [실습 전 사전 준비](#실습-전-사전-준비) (p.37-42)
2. [인증과 권한](#인증과-권한) (p.43-50)
3. [인증 체계 설정](#인증-체계-설정) (p.51-57)
4. [Token 인증 설정](#token-인증-설정) (p.58-63)
5. [Dj-Rest-Auth 라이브러리](#dj-rest-auth-라이브러리) (p.64-74)
6. [Token 발급 및 활용](#token-발급-및-활용) (p.75-86)
7. [권한 정책 설정](#권한-정책-설정) (p.87-98)
8. [Django Signals](#django-signals) (p.99-101)
9. [DRF를 배우는 이유](#drf를-배우는-이유) (p.102-103)

---

## 실습 전 사전 준비

인증 로직을 진행하기 위해 주석 처리되어 있던 User 모델 관련 코드를 되살리는 5단계다 (p.37). 실습 과제이므로 순서를 그대로 따라간다.

### ① user ForeignKey 주석 해제 (p.38)

```python
# articles/models.py
class Article(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### ② serializers의 read_only_fields 주석 해제 (p.39)

```python
# articles/serializers.py
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user',)
```

> **왜 read_only인가** — `user`는 클라이언트가 body로 보내는 값이 아니라 **서버가 인증 정보에서 채워 넣는 값**이다. 읽기 전용으로 두지 않으면 클라이언트가 남의 user id를 실어 보낼 수 있다.

### ③ 게시글 생성 시 user 정보 저장 (p.40)

```python
# articles/views.py
@api_view(['GET', 'POST'])
def article_list(request):
    ...
    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
```

`serializer.save(user=request.user)` — 읽기 전용 필드는 이렇게 `save()`의 인자로 넘겨 채운다.

### ④ session 테스트용 요청 주소 주석 처리 (p.41)

```python
# my_api/urls.py
urlpatterns = [
    ...
    # path('accounts', include('accounts.urls')),
]
```

### ⑤ DB 초기화 (p.42)

1. **DB 초기화**
   - `db.sqlite3` 삭제
   - `migrations` 파일 삭제
2. **Migration 과정 재진행**

---

## 인증과 권한

### Authentication — 인증 (p.43-44)

> **수신된 요청을 해당 요청의 사용자 또는 자격 증명과 연결하는 메커니즘**
> → **누구인지를 확인하는 과정**

### Permissions — 권한 (p.45)

> **요청에 대한 접근 허용 또는 거부 여부를 결정**

### 둘의 순서 (p.46)

- 순서상 **인증이 먼저** 진행되며, 수신 요청을 해당 요청의 사용자 또는 해당 요청이 서명된 토큰(token)과 같은 자격 증명 자료와 연결한다
- **그런 다음** 권한 및 제한 정책은 인증이 완료된 해당 자격 증명을 사용하여 요청을 허용해야 하는지를 결정한다

```text
요청 도착
   │
   ▼
[인증]  누구인가?  ── 자격 증명 식별만 함 (허용/거부 판단 없음)
   │
   ▼
[권한]  이 사람이 접근해도 되는가?  ── 여기서 허용/거부 결정
   │
   ▼
view 함수 본문 실행
```

### DRF에서의 인증 (p.47)

- 인증은 항상 **view 함수 시작 시**, 권한 및 제한 확인이 발생하기 **전**, 다른 코드의 진행이 허용되기 **전**에 실행된다
- **인증 자체로는 들어오는 요청을 허용하거나 거부할 수 없으며**, 단순히 요청에 사용된 자격 증명만 식별한다는 점에 유의

> **시험 포인트** — "인증이 요청을 거부한다"는 서술은 틀렸다. 인증은 **식별만** 하고, 거부 판단은 권한의 몫이다.

### 승인되지 않은 응답과 금지된 응답 (p.48)

인증되지 않은 요청이 권한을 거부하는 경우 해당되는 두 가지 오류 코드를 응답한다.

| 코드 | 이름 | 의미 | 서버가 나를 아는가 |
|---|---|---|---|
| **401** | Unauthorized | 요청된 리소스에 대한 **유효한 인증 자격 증명이 없기 때문에** 클라이언트 요청이 완료되지 않았음을 나타냄 (누구인지를 증명할 자료가 없음) | 모른다 |
| **403** | Forbidden (Permission Denied) | 서버에 요청이 전달되었지만, **권한 때문에 거절**되었다는 것을 의미 | **안다** |

> **핵심 구분** — 401과 403의 차이는 **서버가 클라이언트가 누구인지 알고 있는가**이다. 401은 "당신이 누군지 모르겠다", 403은 "당신이 누군지는 알지만 안 된다"다.

### Session 대신 Token 인증을 사용하는 이유 (p.49-50)

- 세션 기반 인증은 **서버에 세션 데이터를 저장**함 → **상태 저장 방식(stateful)**
- 서버가 사용자의 상태를 유지해야 하므로, 여러 대의 서버를 사용하는 **분산 시스템 구축과 서버 간의 부하 분산이 어려움**
- 토큰 기반 인증은 **RESTful한 방식**으로 클라이언트와 서버 간의 **독립성을 유지**하면서 인증을 처리할 수 있음

→ **RESTful 원칙에 더 부합**한다.

| | 세션 기반 인증 | 토큰 기반 인증 |
|---|---|---|
| 상태 | stateful (서버가 저장) | stateless |
| 저장 위치 | 서버의 `django_session` 테이블 | 클라이언트가 보관, 매 요청에 동봉 |
| 서버 확장 | 분산·부하 분산이 어려움 | 서버 간 독립성 유지 |
| REST 원칙 | 덜 부합 | 더 부합 |

---

## 인증 체계 설정

### 설정 방법 2가지 (p.51-53)

1. **전역 설정**
2. **View 함수 별 설정**

### ① 전역 설정 (p.54)

`DEFAULT_AUTHENTICATION_CLASSES`를 사용한다.

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

문자열 경로로 지정한다는 점에 주의한다.

### ② View 함수 별 설정 (p.55)

`authentication_classes` 데코레이터를 사용한다.

```python
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
def article_list(request):
    pass
```

> **비교** — 전역 설정은 **문자열**로, 데코레이터는 **클래스 객체**로 넘긴다. 두 방식에서 표기법이 다르다는 점이 자주 헷갈린다.

### DRF가 제공하는 인증 체계 (p.56)

1. **BasicAuthentication**
2. **TokenAuthentication** ← 이번 학습에서 사용
3. **SessionAuthentication**
4. **RemoteUserAuthentication**

### TokenAuthentication (p.57)

- **token 기반 HTTP 인증 체계**
- 기본 데스크톱 및 모바일 클라이언트와 같은 **클라이언트-서버 설정에 적합**

→ 서버가 인증된 사용자에게 토큰을 발급하고, 사용자는 매 요청마다 발급받은 토큰을 요청과 함께 보내 인증 과정을 거친다.

---

## Token 인증 설정

### 적용 과정 4단계 (p.58-59)

1. 인증 클래스 설정
2. `INSTALLED_APPS` 추가
3. Migrate 진행
4. 토큰 생성 코드 작성

### ① 인증 클래스 설정 (p.60)

`TokenAuthentication` 활성화 코드 주석 해제. 기본적으로 **모든 view 함수가 토큰 기반 인증이 진행될 수 있도록** 설정하는 것이다.

```python
# settings.py
REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

### ② INSTALLED_APPS 추가 (p.61)

`rest_framework.authtoken` 주석 해제.

```python
# settings.py
INSTALLED_APPS = [
    'articles',
    'accounts',
    'rest_framework',
    'rest_framework.authtoken',
    ...
]
```

### ③ Migrate 진행 (p.62)

`rest_framework.authtoken` 앱이 토큰 저장용 테이블(`authtoken_token`)을 만들어야 하므로 마이그레이션이 필요하다.

```bash
python manage.py migrate
```

### ④ 토큰 생성 코드 작성 (p.63)

`accounts/signals.py` 주석 해제. **새로운 사용자에게 자동으로 토큰을 생성해 주는 역할**이다.

```python
# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
```

> **`if created:`가 핵심** — `post_save`는 생성과 수정 **양쪽 모두**에서 발생한다. `created` 플래그를 확인하지 않으면 사용자 정보를 수정할 때마다 토큰을 또 만들려다 에러가 난다.

---

## Dj-Rest-Auth 라이브러리

### Dj-Rest-Auth란 (p.64-65)

**회원가입, 인증(소셜미디어 인증 등), 비밀번호 재설정, 사용자 세부 정보 검색, 회원 정보 수정** 등 다양한 인증 관련 기능을 제공하는 라이브러리다.

### 설치 및 적용 3단계 (p.66-68)

**1. 설치** (실습 환경에는 사전 설치되어 있음)

```bash
pip install dj-rest-auth
```

**2. 추가 App 주석 해제**

```python
# settings.py
INSTALLED_APPS = [
    'articles',
    'accounts',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    ...
]
```

**3. 추가 URL 주석 해제**

```python
# my_api/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('articles.urls')),
    path('accounts/', include('dj_rest_auth.urls')),
]
```

> **표기 주의** — 설정 파일에서는 언더스코어(`dj_rest_auth`), 패키지 설치명은 하이픈(`dj-rest-auth`)이다.

### Registration(회원가입) 기능 추가 설정 (p.69-74)

`dj_rest_auth`만으로는 회원가입이 되지 않는다. 별도로 4단계를 더 밟아야 한다 (p.69).

1. 패키지 추가 설치
2. 추가 App 등록
3. 추가 URL 등록
4. Migrate

**1. 패키지 추가 설치** (p.70) — 실습 환경에는 사전 설치되어 있고, 의존 버전 다운그레이드도 되어 있다.

```bash
pip install 'dj-rest-auth[with_social]'
```

**2. 추가 App 주석 해제** (p.71)

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    ...
]

SITE_ID = 1
```

**3. 관련 설정 코드 주석 해제** (p.72)

```python
# settings.py
MIDDLEWARE = [
    ...,
    'allauth.account.middleware.AccountMiddleware',
]
```

**4. 추가 URL 주석 해제** (p.73)

```python
# my_api/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('articles.urls')),
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/signup/', include('dj_rest_auth.registration.urls')),
]
```

**5. Migrate 진행** (p.74)

```bash
python manage.py migrate
```

> **자주 놓치는 곳** — `SITE_ID = 1`과 `AccountMiddleware` 두 줄이다. `django.contrib.sites`를 넣고 `SITE_ID`를 빠뜨리면 회원가입 요청에서 에러가 난다.

---

## Token 발급 및 활용

### 추가된 URL 확인 (p.75-77)

라이브러리 설치로 인해 추가된 URL 목록은 `http://127.0.0.1:8000/accounts/`로 접속하면 404 페이지의 URLconf 목록에서 확인할 수 있다.

| URL | name |
|---|---|
| `accounts/password/reset/` | `rest_password_reset` |
| `accounts/password/reset/confirm/` | `rest_password_reset_confirm` |
| `accounts/login/` | `rest_login` |
| `accounts/logout/` | `rest_logout` |
| `accounts/user/` | `rest_user_details` |
| `accounts/password/change/` | `rest_password_change` |
| `accounts/signup/` | — |

### 회원가입과 로그인 (p.78-80)

1. **회원 가입** — `http://127.0.0.1:8000/accounts/signup/` (DRF 페이지 하단 회원 가입 form 사용)
2. **로그인** — `http://127.0.0.1:8000/accounts/login/` (DRF 페이지 하단 로그인 form 사용)
3. 로그인 성공 후 응답으로 **발급된 Token 확인**

```json
{
    "key": "207967dd2adcd336baec971f42bc7cb94b8661ad"
}
```

→ 이제 발급받은 Token을 **매 요청마다 함께 보내야** 한다.

### Token을 사용한 요청 (p.81-83)

Postman으로 `POST http://127.0.0.1:8000/api/v1/articles/`에 게시글 제목과 내용을 담아 요청한다. Headers에 발급받은 Token을 작성해야 `201 Created`가 돌아온다.

| Key | Value |
|---|---|
| `Authorization` | `Token <발급받은 토큰 값>` |

### 클라이언트가 Token으로 인증받는 방법 (p.84)

1. **`Authorization`** HTTP header에 포함시킨다
2. 키 앞에는 문자열 **`Token`**이 와야 하며, **공백**으로 두 문자열을 구분해야 한다

```text
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

> **시험 포인트** — 헤더 이름은 `Authentication`이 아니라 **`Authorization`**이다. 접두어 문자열도 `Bearer`가 아니라 **`Token`**이며, 사이는 **공백 한 칸**이다. 세 가지 모두 오답 선택지로 자주 나온다.

### Token 데이터 확인 (p.85-86)

Django DB의 `authtoken_token` 테이블에서 확인할 수 있다.

| 컬럼 | 타입 |
|---|---|
| `key` | `varchar(40)` |
| `created` | `datetime` |
| `user_id` | `bigint` |

> 발급받은 Token은 **인증이 필요한 요청마다 함께 보내야 한다.**

---

## 권한 정책 설정

### 설정 방법 2가지 (p.87-88)

1. **전역 설정**
2. **View 함수 별 설정**

인증 체계 설정과 구조가 똑같다.

### ① 전역 설정 (p.89)

`DEFAULT_PERMISSION_CLASSES`를 사용한다.

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

지정하지 않을 경우 이 설정은 기본적으로 **무제한 액세스를 허용**한다.

```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.AllowAny',
]
```

### ② View 함수 별 설정 (p.90)

`permission_classes` 데코레이터를 사용한다.

```python
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def article_list(request):
    pass
```

### DRF가 제공하는 권한 정책 (p.91-92)

1. **IsAuthenticated** ← 이번 학습에서 사용
2. **IsAdminUser**
3. **IsAuthenticatedOrReadOnly**
4. ...

**IsAuthenticated 권한** — 인증되지 않은 사용자에 대한 권한을 거부하고, 그렇지 않은 경우 권한을 허용한다.

→ **등록된 사용자만 API에 액세스할 수 있도록** 하려는 경우에 적합하다.

### IsAuthenticated 권한 설정 (p.93-95)

**1. 전역은 AllowAny로 열어둔다** (p.94)

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
```

**2. 필요한 view에만 데코레이터를 건다** (p.95)

전체 게시글 조회 및 생성 시에만 인증된 사용자만 진행할 수 있도록 권한을 설정한다.

```python
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def article_list(request):
    pass
```

> **설계 의도** — 전역은 `AllowAny`로 열어두고, 보호가 필요한 view에만 `IsAuthenticated`를 거는 방식이다. 반대로 전역을 잠그고 예외를 여는 방식도 가능하며, 어느 쪽이든 **전역 설정과 데코레이터가 충돌하면 데코레이터가 이긴다.**

### 권한 활용 — 403을 직접 만들어 보기 (p.96-98)

관리자만 전체 게시글 조회가 가능한 권한이 설정되었을 때, **인증된 일반 사용자**가 조회 요청을 하면 어떤 응답이 오는지 확인하는 실습이다.

**1. 임시로 `IsAdminUser`로 변경** (p.96)

```python
# articles/views.py
from rest_framework.permissions import IsAuthenticated, IsAdminUser

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def article_list(request):
    pass
```

**2. 전체 게시글 조회 요청** (p.97)

`GET http://127.0.0.1:8000/api/v1/articles/` → **403 Forbidden** 응답 확인.

토큰은 유효하므로 서버는 내가 누구인지 안다. 다만 관리자가 아니어서 거절당한 것이다. 401이 아니라 403이 나오는 이유가 여기에 있다.

**3. IsAuthenticated 권한으로 복구** (p.98)

```python
# articles/views.py
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def article_list(request):
    pass
```

---

## Django Signals

### 개념 (p.99-100)

**"이벤트 알림 시스템"**

- 애플리케이션 내에서 **특정 이벤트가 발생할 때, 다른 부분에게 신호를 보내어** 이벤트가 발생했음을 알릴 수 있음
- 주로 **모델의 데이터 변경 또는 저장, 삭제와 같은 작업에 반응하여** 추가적인 로직을 실행하고자 할 때 사용
  - 예를 들어, 사용자가 새로운 게시글을 작성할 때마다 특정 작업(예: 이메일 알림 보내기)을 수행하려는 경우

### 이번 프로젝트에서의 사용 (p.101)

앞서 4단계에서 작성한 토큰 자동 생성 코드가 바로 Signals의 활용 사례다.

```python
# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
```

```text
User 객체 저장(save)
        │
        ▼  post_save 시그널 발생
@receiver 가 등록한 create_auth_token 실행
        │
        ▼  created == True 인 경우에만
Token.objects.create(user=instance)
```

| 구성 요소 | 역할 |
|---|---|
| `post_save` | 모델 저장 **후**에 발생하는 내장 시그널 |
| `@receiver` | 이 함수를 해당 시그널의 수신자로 등록하는 데코레이터 |
| `sender` | 어떤 모델의 시그널을 받을지 지정 (`settings.AUTH_USER_MODEL`) |
| `created` | 신규 생성이면 `True`, 기존 객체 수정이면 `False` |
| `instance` | 방금 저장된 모델 객체 (여기서는 User) |

---

## DRF를 배우는 이유

이번 학습을 마무리하며 정리하는 세 가지다 (p.102-103).

**1. 백엔드와 프론트엔드의 분리 경험**
기존 Django 템플릿 기반의 서버 렌더링 방식을 벗어나, 백엔드(데이터·로직)와 프론트엔드(UI)를 명확히 분리하는 패턴을 간접적으로 체험했다.

**2. 표준화된 API 구축 역량 확보**
DRF를 통해 RESTful API를 손쉽게 만들고 관리하는 방법을 학습했는데, 이는 다양한 클라이언트(웹, 모바일 앱, 외부 서비스)와 연동하는 데 필수적인 능력이다.

**3. 프론트엔드 기술과의 연결 고리**
앞으로 학습할 JavaScript 및 Vue는 주로 API를 통해 데이터를 받아와 화면을 구성한다. DRF로 구축한 일관된 API는 Vue 등 프론트엔드 프레임워크와 매끄럽게 호환된다.

---

## 정리 체크리스트

- [ ] 인증과 권한의 정의를 각각 한 문장으로 말할 수 있다
- [ ] 인증과 권한 중 무엇이 먼저 실행되는지, 인증이 요청을 거부할 수 있는지 답할 수 있다
- [ ] 401과 403의 차이를 "서버가 누구인지 아는가" 기준으로 설명할 수 있다
- [ ] 세션 인증 대신 토큰 인증을 쓰는 이유를 stateful/stateless로 설명할 수 있다
- [ ] 인증 체계를 전역과 View 단위로 설정하는 코드를 각각 쓸 수 있다
- [ ] DRF가 제공하는 인증 체계 4가지를 나열할 수 있다
- [ ] TokenAuthentication 적용 4단계를 순서대로 말할 수 있다
- [ ] `signals.py`의 토큰 자동 생성 코드를 보고 각 요소의 역할을 설명할 수 있다
- [ ] `if created:`가 왜 필요한지 설명할 수 있다
- [ ] Dj-Rest-Auth의 Registration 추가 설정 4단계를 말할 수 있다
- [ ] 토큰을 실어 보내는 헤더 이름과 접두어 형식을 정확히 쓸 수 있다
- [ ] `authtoken_token` 테이블의 세 컬럼을 말할 수 있다
- [ ] DRF 권한 정책 3가지의 이름과 동작을 구분할 수 있다

## 복습 문제

**1.** 인증(Authentication)과 권한(Permissions)의 정의를 각각 쓰시오.

<details>
<summary>답</summary>

- **인증** — 수신된 요청을 해당 요청의 사용자 또는 자격 증명과 연결하는 메커니즘. 누구인지를 확인하는 과정.
- **권한** — 요청에 대한 접근 허용 또는 거부 여부를 결정.

</details>

**2.** 다음 서술의 참·거짓을 판별하고 이유를 쓰시오. "DRF의 인증은 유효하지 않은 요청을 거부한다."

<details>
<summary>답</summary>

**거짓.** 인증 자체로는 들어오는 요청을 허용하거나 거부할 수 없으며, **단순히 요청에 사용된 자격 증명만 식별**한다. 허용·거부 판단은 그다음 단계인 권한 및 제한 정책이 수행한다.

</details>

**3.** 401 Unauthorized와 403 Forbidden의 차이를 서버 관점에서 설명하시오.

<details>
<summary>답</summary>

- **401 Unauthorized** — 요청된 리소스에 대한 유효한 인증 자격 증명이 없어 요청이 완료되지 않음. 서버는 **클라이언트가 누구인지 모른다.**
- **403 Forbidden** — 요청은 서버에 전달되었으나 권한 때문에 거절됨. 401과 달리 서버는 **클라이언트가 누구인지 알고 있다.**

</details>

**4.** 세션 기반 인증 대신 토큰 기반 인증을 사용하는 이유를 세 가지로 쓰시오.

<details>
<summary>답</summary>

1. 세션 기반 인증은 서버에 세션 데이터를 저장하는 **상태 저장 방식(stateful)**이다.
2. 서버가 사용자의 상태를 유지해야 하므로 **여러 대의 서버를 사용하는 분산 시스템 구축과 서버 간 부하 분산이 어렵다.**
3. 토큰 기반 인증은 **RESTful한 방식**으로 클라이언트와 서버 간의 독립성을 유지하면서 인증을 처리할 수 있어 **RESTful 원칙에 더 부합**한다.

</details>

**5.** DRF가 제공하는 인증 체계 4가지를 쓰시오.

<details>
<summary>답</summary>

1. BasicAuthentication
2. TokenAuthentication
3. SessionAuthentication
4. RemoteUserAuthentication

</details>

**6.** 전역 설정으로 TokenAuthentication을 적용하는 `settings.py` 코드를 쓰시오.

<details>
<summary>답</summary>

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

</details>

**7.** TokenAuthentication 적용 과정 4단계를 순서대로 쓰시오.

<details>
<summary>답</summary>

1. 인증 클래스 설정
2. `INSTALLED_APPS` 추가 (`rest_framework.authtoken`)
3. Migrate 진행
4. 토큰 생성 코드 작성

</details>

**8.** 아래 코드의 빈칸을 채우시오. 새로운 사용자에게 자동으로 토큰을 생성해 주는 코드다.

```python
from django.db.models.signals import ______
from django.dispatch import ______
from rest_framework.authtoken.models import Token
from django.conf import settings

@______(______, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if ______:
        Token.objects.create(user=instance)
```

<details>
<summary>답</summary>

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
```

`if created:`가 없으면 사용자 정보를 **수정**할 때마다 토큰을 또 만들려고 시도한다.

</details>

**9.** 발급받은 토큰을 요청에 실어 보낼 때의 헤더 Key와 Value 형식을 정확히 쓰시오.

<details>
<summary>답</summary>

- Key: **`Authorization`**
- Value: **`Token <토큰 값>`** — 문자열 `Token` 뒤에 **공백 한 칸**으로 구분한다.

```text
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

</details>

**10.** DRF에서 권한을 View 함수 단위로 설정할 때 사용하는 데코레이터와, 전역 설정 시 사용하는 키 이름을 각각 쓰시오.

<details>
<summary>답</summary>

- View 단위: **`@permission_classes([...])`**
- 전역: **`DEFAULT_PERMISSION_CLASSES`**

인증의 경우는 각각 `@authentication_classes([...])`, `DEFAULT_AUTHENTICATION_CLASSES`다.

</details>

**11.** `DEFAULT_PERMISSION_CLASSES`를 지정하지 않으면 기본 동작은 무엇이며, 그것을 명시적으로 쓰면 어떤 클래스인가?

<details>
<summary>답</summary>

지정하지 않으면 기본적으로 **무제한 액세스를 허용**한다. 명시적으로 쓰면 **`rest_framework.permissions.AllowAny`**다.

</details>

**12.** `authtoken_token` 테이블의 컬럼 세 개를 타입과 함께 쓰시오.

<details>
<summary>답</summary>

| 컬럼 | 타입 |
|---|---|
| `key` | `varchar(40)` |
| `created` | `datetime` |
| `user_id` | `bigint` |

</details>

**13.** Dj-Rest-Auth의 Registration 기능을 추가할 때 `INSTALLED_APPS`에 넣어야 하는 앱들과, 함께 설정해야 하는 변수 한 줄을 쓰시오.

<details>
<summary>답</summary>

```python
INSTALLED_APPS = [
    ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    ...
]

SITE_ID = 1
```

그리고 `MIDDLEWARE`에 `'allauth.account.middleware.AccountMiddleware'`를 추가해야 한다.

</details>

**14.** 인증된 일반 사용자가 `@permission_classes([IsAdminUser])`가 걸린 view에 요청을 보내면 어떤 상태 코드가 응답되는가? 그 이유는?

<details>
<summary>답</summary>

**403 Forbidden.** 토큰이 유효하므로 인증은 성공했고 서버는 클라이언트가 누구인지 **알고 있다.** 다만 관리자가 아니어서 권한 단계에서 거절된 것이므로 401이 아니라 403이다.

</details>

---

> **읽은 방식 메모** — 이 노트의 코드 블록(p.38, 41, 54, 60, 63, 71, 72, 89, 94, 96)과 헤더 형식(p.84), DB 테이블 구조(p.85)는 원본 슬라이드를 2000px 이상으로 재렌더링해 육안 대조를 마쳤다. 나머지 코드 페이지(p.39, 40, 55, 61, 67, 68, 73, 90, 95, 98, 101)와 한국어 설명문은 3200px 재-OCR 결과를 문맥으로 복원한 것이다. 영문 코드는 고정폭 폰트라 인식률이 높지만, 한국어 서술문에는 조사·어미 수준의 미세한 표현 차이가 있을 수 있다. `pip install` 명령(p.66, p.70)과 `migrate` 명령(p.62, p.74)은 슬라이드에 화면 캡처로만 제시된 부분이라 표준 명령어로 보충해 적었다.
