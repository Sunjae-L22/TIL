# Django Web Framework

> 출처: `16기_데이터트랙_0729_Django_WebFramework.pdf` (총 151페이지) · 정리일: 2026-07-29
> 페이지 표기는 PDF 기준 (슬라이드 인쇄 번호와 동일)

## 한눈에 보기

- 웹은 **요청(request)과 응답(response)** 으로 돌아간다. 이 구조에서 Django는 어느 자리에 서는가?
- 왜 가상환경을 만들고 `requirements.txt`를 관리해야 하는가? 안 하면 무엇이 깨지는가?
- MVC와 MTV는 무엇이 다른가? (힌트: 실질적으로는 다르지 않다)
- REST API에서 자원을 다루는 세 가지 축 — **식별(URI) / 행위(HTTP Method) / 표현(JSON)** 을 설명할 수 있는가?
- 요청이 들어왔을 때 `urls.py` → `views.py` → 응답까지, 코드로 그 경로를 직접 그릴 수 있는가?
- URL에 변수를 담고(Variable Routing), 앱별로 URL을 쪼개는(`include`) 이유는?

## 목차

1. [Web Application](#web-application) (p.4-19)
2. [Django Framework와 가상환경](#django-framework와-가상환경) (p.20-49)
3. [Django Design Pattern](#django-design-pattern) (p.51-70)
4. [REST API](#rest-api) (p.72-107)
5. [요청과 응답](#요청과-응답) (p.109-124)
6. [Variable Routing](#variable-routing) (p.125-131)
7. [App과 URL 분리](#app과-url-분리) (p.132-139)
8. [request 객체와 MTV 정리](#request-객체와-mtv-정리) (p.140-150)

---

## Web Application

### 웹 애플리케이션 개발이란 (p.5-6)

인터넷을 통해 사용자에게 제공되는 소프트웨어 프로그램을 구축하는 과정이다. 모바일·태블릿·PC 등 다양한 디바이스에서 **웹 브라우저를 통해 접근**하고 사용할 수 있다는 점이 데스크톱 애플리케이션과의 결정적 차이다.

### 클라이언트-서버 구조 (p.7-13)

웹의 동작 방식은 두 주체의 대화로 요약된다.

```text
        ── requests ──▶
CLIENT                    SERVER
        ◀── responses ──
```

| 주체 | 정의 | 실체 |
|---|---|---|
| **Client (클라이언트)** | 서비스를 요청하는 주체 | 웹 사용자의 인터넷이 연결된 장치, 웹 브라우저 |
| **Server (서버)** | 클라이언트의 요청에 응답하는 주체 | 웹 페이지·앱을 저장하는 컴퓨터 |

**우리가 웹 페이지를 보게 되는 과정**

1. 웹 브라우저(클라이언트)에서 `google.com`을 입력
2. 브라우저는 인터넷에 연결된 전세계 어딘가에 있는 구글 컴퓨터(서버)에게 'Google 홈페이지.html' 파일을 달라고 요청
3. 요청을 받은 구글 컴퓨터는 데이터베이스에서 'Google 홈페이지.html' 파일을 찾아 응답
4. 전달받은 'Google 홈페이지.html' 파일을 사람이 볼 수 있도록 웹 브라우저가 해석해주면서 사용자는 구글의 메인 페이지를 보게 됨

> **핵심** — 서버는 "파일 혹은 데이터를 주는 쪽", 브라우저는 "받아서 해석해 그려주는 쪽"이다. 이 역할 분담이 뒤에 나올 Frontend/Backend 구분의 뿌리다.

### Frontend & Backend (p.14-18)

| 구분 | 하는 일 | 기술 스택 |
|---|---|---|
| **Frontend (프론트엔드)** | 사용자 인터페이스(UI)를 구성하고, 사용자가 애플리케이션과 상호작용할 수 있도록 함 | HTML, CSS, JavaScript, 프론트엔드 프레임워크 |
| **Backend (백엔드)** | 서버 측에서 동작하며, 클라이언트의 요청에 대한 처리와 데이터베이스와의 상호작용 등을 담당 | 서버 언어(Python, Java 등), 백엔드 프레임워크, 데이터베이스, API, 보안 |

구조를 그림으로 옮기면 이렇다.

```text
Client ◀──▶ [Front-end Framework] ◀──▶ Server (Django)
                (React/Angular/Vue)      └─────────────┘
                                            Backend
```

> **이 과목에서의 위치** — 우리는 이 그림의 오른쪽, 즉 **Backend를 Django로 구현**한다. Front-end Framework 자리는 Vue 등이 담당한다.

---

## Django Framework와 가상환경

### 왜 Web Framework인가 (p.22-23)

웹 서비스 개발에는 로그인, 로그아웃, 회원관리, 데이터베이스, 보안 등 너무 많은 기술이 필요하다. 하나부터 열까지 개발자가 모두 작성하는 것은 현실적으로 어렵다. 하지만 모든 걸 직접 만들 필요가 없다 — **잘 만들어진 것들을 가져와 좋은 환경에서 내 것으로 잘 사용하는 것도 능력인 시대**다.

**Web Framework** = 웹 애플리케이션을 빠르게 개발할 수 있도록 도와주는 도구. 개발에 필요한 기본 구조, 규칙, 라이브러리 등을 제공한다.

### Django를 사용하는 이유 (p.25-28)

Django는 **Python 기반의 대표적인 웹 프레임워크**다.

| 장점 | 내용 |
|---|---|
| **다양성** | Python 기반으로 소셜 미디어 및 빅데이터 관리 등 광범위한 서비스 개발에 적합 |
| **확장성** | 대량의 데이터에 대해 빠르고 유연하게 확장할 수 있는 기능을 제공 |
| **보안** | 취약점으로부터 보호하는 보안 기능이 기본적으로 내장되어 있음 |
| **커뮤니티 지원** | 개발자를 위한 지원, 문서 및 업데이트를 제공하는 활성화된 커뮤니티 |

검증된 프레임워크라는 근거로 Spotify, Instagram, Dropbox, Delivery Hero 등 대규모 서비스 사례가 제시된다. 2023년 기준 인기 Backend Framework 순위는 1. Laravel, 2. **Django**, 3. Spring, 4. Flask, 5. Express JS.

### 가상 환경 (p.31-35)

**가상 환경(Virtual Environment)** = Python 애플리케이션과 그에 따른 패키지들을 **격리하여 관리**할 수 있는 독립적인 실행 환경.

```text
Python global 환경
├── 가상 환경 A          ├── 가상 환경 B
│   requests 3.4         │   requests 2.2
│   Django 2.2           │   Django 5.2
│   beautifulsoup 7.1    │   pandas 7.1
│   ...                  │   ...
```

**시나리오 1 — 버전 충돌**

1. 한 개발자가 2개의 프로젝트(A와 B)를 진행해야 한다.
2. 프로젝트 A는 requests 패키지 버전 1을 사용해야 한다.
3. 프로젝트 B는 requests 패키지 버전 2를 사용해야 한다.
4. 하지만 파이썬 환경에서 패키지는 1개의 버전만 존재할 수 있다.
5. A와 B 프로젝트의 다른 패키지 버전 사용을 위한 독립적인 개발 환경이 필요하다.

**시나리오 2 — 패키지 간 충돌**

1. 한 개발자가 2개의 프로젝트(A와 B)를 진행해야 한다.
2. 프로젝트 A는 water 패키지를 사용해야 한다.
3. 프로젝트 B는 fire 패키지를 사용해야 한다.
4. 하지만 파이썬 환경에서 water 패키지와 fire 패키지를 함께 사용하면 충돌이 발생하기 때문에 설치할 수 없다.
5. A와 B 프로젝트의 패키지 충돌을 피하기 위해 각각 독립적인 개발 환경이 필요하다.

### 가상 환경 다루기 (p.36-38)

**1. 가상 환경 venv 생성**

```bash
$ python -m venv venv
```

**2. 가상 환경 활성화**

```bash
$ source venv/Scripts/activate
```

**3. 환경에 설치된 패키지 목록 확인**

```bash
$ pip list
```

```text
Package    Version
---------- -------
pip        23.0.1
setuptools 58.1.0
```

> **주의** — `python -m venv venv`에서 뒤쪽 `venv`는 **생성될 폴더 이름**이다. 앞의 `venv`는 모듈 이름. 같은 단어라 헷갈리기 쉽다.

### 의존성 패키지와 requirements.txt (p.39-44)

**패키지 목록이 필요한 이유**

- 만약 2명(A와 B)의 개발자가 하나의 프로젝트를 함께 개발한다고 하자.
- 팀원 A가 먼저 가상 환경을 생성 후 프로젝트를 설정하고 관련된 패키지를 설치하고 개발하다가, 협업을 위해 GitHub에 프로젝트를 push 한다.
- 팀원 B는 해당 프로젝트를 clone 받고 실행해보려 하지만 실행되지 않는다.
- 팀원 A가 이 프로젝트를 위해 어떤 패키지를 설치했고, 어떤 버전을 설치했는지 A의 가상 환경 정보를 알 수 없다.
- 가상 환경에 대한 정보, 즉 **패키지 목록이 공유되어야 한다.**

**의존성 패키지(dependency)** — 한 소프트웨어 패키지가 다른 패키지의 기능이나 데이터를 사용하기 때문에 그 패키지가 존재해야만 제대로 작동하는 관계. 사용하려는 패키지가 설치되지 않았거나 호환되는 버전이 아니면 오류가 발생하거나 예상치 못한 동작을 보일 수 있다.

`requests` 하나를 설치하면 실제로는 여러 패키지가 함께 깔린다.

```text
설치 전                        설치 후
Package    Version             Package            Version
---------- -------             ------------------ ----------
pip        23.0.1              certifi            2023.11.17
setuptools 58.1.0              charset-normalizer 3.3.2
                               idna               3.6
                               pip                23.0.1
                               requests           2.31.0
                               setuptools         58.1.0
                               urllib3            2.1.0
```

**4. 의존성 패키지 목록 생성**

```bash
$ pip freeze > requirements.txt
```

**[번외] 패키지 목록 기반 설치** — 처음부터 `requirements.txt`를 받은 상태로 진행하는 경우, 가상환경 활성화 후 `requirements.txt` 기반으로 패키지 설치가 필요하다. (가상환경 폴더 `venv`는 `.gitignore`에 의해 공유되지 않음)

```bash
$ pip install -r requirements.txt
```

> **시험 포인트** — `venv` 폴더는 git에 올리지 않는다. 대신 `requirements.txt`를 올린다. "왜 clone 받은 프로젝트가 실행이 안 되는가"의 답은 대부분 여기다.

### Django 프로젝트 생성 루틴 (p.46-49)

프로젝트를 시작할 때마다 반복하는 4단계다.

```bash
# 1. 가상환경(venv) 생성
$ python -m venv venv

# 2. 가상환경 활성화
$ source venv/Scripts/activate

# 3. Django 설치
$ pip install django

# 4. 의존성 목록 생성  (패키지 설치시마다 진행)
$ pip freeze > requirements.txt
```

> **주의** — Python 3.10 이상일 경우 Django 5 버전이 설치되니 주의.

**Django 프로젝트 생성**

```bash
$ django-admin startproject firstpjt .
```

`firstpjt` 라는 이름의 프로젝트를 생성한다.

**Django 서버 실행**

```bash
$ python manage.py runserver
```

> **주의** — `manage.py`와 동일한 경로에서 진행해야 한다.

실행 후 `http://127.0.0.1:8000/` 에 접속하면 "The install worked successfully! Congratulations!" 축하 페이지가 뜬다. 이 페이지가 보이는 이유는 settings 파일에서 `DEBUG=True`이고 아직 URL을 하나도 설정하지 않았기 때문이다.

---

## Django Design Pattern

### 디자인 패턴과 MVC (p.53-55)

**디자인 패턴** = 소프트웨어 설계에서 발생하는 문제를 해결하기 위한 일반적인 해결책. 공통적인 문제를 해결하는 데 쓰이는 형식화된 관행이며, 쉽게 말해 "애플리케이션의 구조는 이렇게 구성하자"는 관행이다.

**MVC 디자인 패턴 (Model, View, Controller)** — 애플리케이션을 구조화하는 대표적인 패턴. "데이터" & "사용자 인터페이스" & "비즈니스 로직"을 분리한다.

왜 분리하는가? **시각적 요소와 뒤에서 실행되는 로직을 서로 영향 없이, 독립적이고 쉽게 유지 보수할 수 있는 애플리케이션을 만들기 위해서**다.

### MTV 디자인 패턴 (p.56-57)

Django에서 애플리케이션을 구조화하는 패턴. 기존 MVC 패턴과 **동일하나 단순히 명칭을 다르게 정의한 것**이다.

```text
MVC              MTV
─────────────────────────
Model      →     Model
View       →     Template
Controller →     View
```

> **가장 헷갈리는 지점** — MVC의 View와 MTV의 View는 **완전히 다른 것**을 가리킨다. MTV의 View는 MVC의 Controller에 해당한다. 시험에서 노리는 함정이다.

### Project와 App (p.59-62)

| 개념 | 정의 |
|---|---|
| **Django project** | 애플리케이션의 집합 (DB 설정, URL 연결, 전체 앱 설정 등을 처리) |
| **Django application** | 독립적으로 작동하는 기능 단위 모듈 (각자 특정한 기능을 담당하며 다른 앱과 함께 하나의 프로젝트를 구성) |

**만약 온라인 커뮤니티 카페를 만든다면?**

| | 프로젝트 | 앱 |
|---|---|---|
| 예시 | 카페 | 게시글, 댓글, 회원 관리 등 |
| 역할 | 전체 설정 담당 | DB, 인증, 화면 |

### 앱을 사용하기 위한 순서 (p.63-65)

**1. 앱 생성** — 앱의 이름은 '복수형'으로 지정하는 것을 권장한다.

```bash
$ python manage.py startapp articles
```

**2. 앱 등록** — 반드시 **앱을 생성한 후에 등록**해야 한다. (등록 후 생성은 불가능)

```python
# settings.py

INSTALLED_APPS = [
    'articles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

> **주의** — 생성 → 등록 순서를 반드시 지킬 것. 순서를 바꾸면 동작하지 않는다. 또한 직접 만든 앱은 관례적으로 리스트 **맨 위**에 적는다.

### 프로젝트 구조 (p.66-68)

```text
firstpjt/
├── __init__.py     해당 폴더를 패키지로 인식하도록 설정하는 파일
├── asgi.py         비동기식 웹 서버와의 연결 관련 설정  (수정할 일 없음)
├── settings.py     프로젝트의 모든 설정을 관리          ★
├── urls.py         요청 들어오는 URL에 따라 이에 해당하는 적절한 views를 연결  ★
└── wsgi.py         웹 서버와의 연결 관련 설정
manage.py           Django 프로젝트와 다양한 방법으로 상호작용 하는
                    커맨드라인 유틸리티  (수정할 일 없음)
```

★ 표시가 수업 중 실제로 건드리는 파일이다.

### 앱 구조 (p.69-70)

```text
articles/
├── migrations/     DB 변경 이력 (자동 생성)
├── __init__.py
├── admin.py        관리자용 페이지 설정                              ★
├── apps.py         앱의 정보가 작성된 곳            (수정할 일 없음)
├── models.py       DB와 관련된 Model을 정의 — MTV 패턴의 M           ★
├── tests.py        프로젝트 테스트 코드를 작성하는 곳 (수정할 일 없음)
└── views.py        HTTP 요청을 처리하고 해당 요청에 대한 응답을 반환
                    (url, model, template과 연계) — MTV 패턴의 V     ★
```

> **매핑 정리** — `models.py` = **M**odel, `views.py` = **V**iew, 그리고 Template은 별도의 `templates/` 폴더에 `.html` 파일로 존재한다. 앱 폴더에 `urls.py`와 `templates/`는 **기본으로 생성되지 않으므로 직접 만들어야 한다.**

---

## REST API

### API란 (p.74-80)

**API (Application Programming Interface)** = 두 소프트웨어가 서로 통신할 수 있게 하는 메커니즘. 클라이언트-서버처럼 서로 다른 프로그램에서 요청과 응답을 받을 수 있도록 만든 체계다.

**예시 — 기상청 시스템**

- 기상 데이터가 들어있는 기상청의 시스템이 있다.
- 스마트폰의 날씨 앱, 웹 사이트의 날씨 정보 등 다양한 서비스들이 이 기상청 시스템으로부터 데이터를 요청해서 받아 간다.
- 날씨 데이터를 얻으려면? 기상청 시스템에는 정보들을 요청하는 **지정된 형식**이 있다. 지역, 날짜, 조회할 내용들(온도, 바람 등)을 제공하는 매뉴얼이다.
- 즉 "이렇게 요청을 보내면, 이렇게 정보를 제공해줄 것이다"라는 매뉴얼 = **API**.

**API의 역할 — 냉장고 비유**

우리 집 냉장고에 전기를 공급해야 한다고 가정해보자. 우리는 그냥 냉장고의 플러그를 소켓에 꽂으면 제품이 작동한다. 중요한 것은 우리가 가전 제품에 **"전기를 공급하기 위해 직접 배선을 하지 않는다"** 는 것이다. 이는 매우 위험하면서도 비효율적인 일이기 때문이다.

> **복잡한 코드를 추상화하여 대신 사용할 수 있는 몇 가지 더 쉬운 구문을 제공하는 것** — 이것이 API다.

**Web API** — 웹 서버 또는 웹 브라우저를 위한 API. 현대 웹 개발은 하나부터 열까지 직접 개발하기보다 여러 Open API들을 활용하는 추세다. 대표적인 3rd Party Open API 서비스로 Youtube API, Google Map API, Naver Papago API, Kakao Map API 등이 있다.

### REST와 RESTful API (p.81-85)

**REST (Representational State Transfer)** = API Server를 개발하기 위한 일종의 소프트웨어 설계 **"방법론"**.

등장 배경은 단순하다 — "모두가 API Server를 설계하는 구조가 다르니, 이렇게 맞춰서 설계하는 게 어때?"라는 제안이었다.

**RESTful API** — REST 원리를 따르는 시스템을 'RESTful 하다'고 부른다. "자원을 정의"하고 "자원에 대한 주소를 지정"하는 전반적인 방법을 서술한다.

**REST API** = REST라는 설계 디자인 약속을 지켜 구현한 API. 실제 Naver Cloud Platform, Kakao 로그인 등 상용 API 문서가 모두 "RESTful API로 제공되며 JSON 형식으로 응답합니다" 식으로 기술되어 있다.

### 자원을 사용하는 3가지 축 (p.86)

REST에서 자원을 사용하는 법은 딱 세 가지로 정리된다. **이 표가 REST 챕터 전체의 뼈대다.**

| 축 | 무엇으로 | 설명 |
|---|---|---|
| 1. 자원의 **"식별"** | URI | 어떤 자원인가 |
| 2. 자원의 **"행위"** | HTTP Methods | 그 자원에 무엇을 하려는가 |
| 3. 자원의 **"표현"** | JSON 데이터 | 어떤 형태로 주고받는가 |

### 1. 자원의 식별 — URI와 URL (p.88-96)

**URI (Uniform Resource Identifier, 통합 자원 식별자)** — 인터넷에서 리소스(자원)를 식별하는 문자열. 가장 일반적인 URI는 웹 주소로 알려진 **URL**이다.

**URL (Uniform Resource Locator, 통합 자원 위치)** — 웹에서 주어진 리소스의 주소. 네트워크 상에 리소스가 어디 있는지를 알려주기 위한 약속이다.

```text
http:// www.example.com : 80 /path/to/myfile.html ?key1=value1&key2=value2 #SomewhereInTheDocument
└─┬──┘ └───────┬──────┘ └┬┘ └────────┬─────────┘ └───────────┬──────────┘ └──────────┬────────┘
Scheme    Domain Name   Port    Path to the file          Parameters               Anchor
       └────────── Authority ─────────┘
```

| 구성 요소 | 설명 |
|---|---|
| **Scheme (Protocol)** | 브라우저가 리소스를 요청하는 데 사용해야 하는 규약. URL의 첫 부분은 브라우저가 어떤 규약을 사용하는지를 나타냄. 기본적으로 웹은 `http(s)`를 요구하며, 메일을 열기 위한 `mailto:`, 파일을 전송하기 위한 `ftp:` 등 다른 프로토콜도 존재 |
| **Domain Name** | 요청 중인 웹 서버를 나타냄. 어떤 웹 서버가 요구되는지를 가리키며 직접 IP 주소를 사용하는 것도 가능하지만, 사람이 외우기 어렵기 때문에 주로 Domain Name으로 사용. 예를 들어 도메인 `google.com`의 IP 주소는 `142.251.42.142` |
| **Port** | 웹 서버의 리소스에 접근하는 데 사용되는 기술적인 문(Gate). HTTP 프로토콜의 표준 포트는 **HTTP - 80**, **HTTPS - 443**. 표준 포트만 작성 시 생략 가능 |
| **Path** | 웹 서버의 리소스 경로. 과거에는 실제 파일이 위치한 물리적 위치를 나타냈지만, 오늘날은 실제 위치가 아닌 **추상화된 형태의 구조를 표현**. 예를 들어 `/articles/create/`라는 주소가 실제 articles 폴더 안에 create 폴더를 나타내는 것은 아님 |
| **Parameters** | 웹 서버에 제공하는 추가적인 데이터. `&` 기호로 구분되는 key-value 쌍 목록. 서버는 리소스를 응답하기 전에 이러한 파라미터를 사용하여 추가 작업을 수행할 수 있음 |
| **Anchor** | 일종의 "북마크"를 나타내며 브라우저에 해당 지점에 있는 콘텐츠를 표시. **fragment identifier(부분 식별자)** 라고 부르는 `#` 이후 부분은 **서버에 전송되지 않음** |

> **시험 포인트** — Anchor(`#` 뒤쪽)는 **서버로 전송되지 않는다**. `https://docs.djangoproject.com/en/5.2/intro/install/#quick-install-guide` 요청에서 `#quick-install-guide`는 서버에 전달되지 않고, 브라우저에게 해당 지점으로 이동하라고 알려줄 뿐이다.

### 2. 자원의 행위 — HTTP Request Methods (p.98-101)

**HTTP Request Methods** = 리소스에 대한 행위(수행하고자 하는 동작)를 정의. HTTP verbs 라고도 한다.

| Method | 역할 |
|---|---|
| **GET** | 서버에 리소스의 표현을 요청. GET을 사용하는 요청은 **데이터만 검색**해야 함 |
| **POST** | 데이터를 지정된 리소스에 제출. **서버의 상태를 변경** |
| **PUT** | 요청한 주소의 리소스를 수정 |
| **DELETE** | 지정된 리소스를 삭제 |

**HTTP response status codes** — 특정 HTTP 요청이 성공적으로 완료되었는지 여부를 나타낸다. 5개의 그룹으로 나뉜다.

| 범위 | 그룹 |
|---|---|
| 100-199 | Informational responses |
| 200-299 | Successful responses |
| 300-399 | Redirection messages |
| 400-499 | Client error responses |
| 500-599 | Server error responses |

> **암기 팁** — 4xx는 **너(클라이언트)** 잘못, 5xx는 **나(서버)** 잘못.

### 3. 자원의 표현 — JSON (p.103-107)

**현재 Django가 응답(자원을 표현)하는 것**

- Django는 Full Stack framework에 속하기 때문에 기본적으로 사용자에게 **페이지(html)** 를 응답한다.
- 하지만 서버가 응답할 수 있는 것은 페이지 뿐만 아니라 다양한 데이터 타입을 응답할 수 있다.
- **REST API는 이 중에서도 JSON 타입으로 응답하는 것을 권장**한다.

**응답 데이터 타입의 변화**

```text
[1단계] 페이지(html)만을 응답했던 서버
   Client ◀── html ── Server

[2단계] 이제는 JSON 데이터를 응답하는 REST API 서버로의 변환
   Client ◀── JSON ── Server

[3단계] Django는 더 이상 Template 부분에 대한 역할을 담당하지 않게 되며,
        본격적으로 Front-end와 Back-end가 분리되어 구성 됨
   Client ◀──▶ [Front-end Framework] ◀── JSON ── Server (Django)

[4단계] 이제부터 Django를 사용해 RESTful API 서버를 구축할 것
```

> **이 흐름이 과목 전체의 방향 전환점이다.** Django가 HTML을 만들어 보내주던 시대에서, JSON만 던져주고 화면은 프론트엔드에 맡기는 시대로 넘어간다. 그래서 뒤에 나오는 view 함수들이 전부 `JsonResponse`를 반환한다.

---

## 요청과 응답

### Django REST framework (DRF) (p.111-113)

**DRF** = Django에서 RESTful API 서버를 쉽게 구축할 수 있도록 도와주는 **오픈소스 라이브러리**.

**사전 준비 (1/2)**

```bash
# 가상환경(venv) 생성
$ python -m venv venv

# 가상환경 활성화
$ source venv/Scripts/activate

# Django 설치
$ pip install Django
```

**사전 준비 (2/2)**

```bash
$ pip install djangorestframework
```

```python
# settings.py

INSTALLED_APPS = [
    'rest_framework',
]
```

```bash
$ pip freeze > requirements.txt
```

> **패턴 확인** — DRF도 결국 하나의 앱이다. 설치 → `INSTALLED_APPS` 등록 → `requirements.txt` 갱신. 앞에서 배운 순서 그대로다.

### Django URLs의 역할 (p.115-117)

요청과 응답의 흐름 안에서 `urls.py`가 서 있는 자리는 이렇다.

```text
requests ──▶ project
              └── urls ──▶ views
```

**URL dispatcher (운항 관리자, 분배기)** = URL 패턴을 정의하고, 해당 패턴이 일치하는 요청을 처리할 **view 함수를 연결(매핑)** 한다.

### 1. URLs 작성 (p.118-120)

```python
# firstpjt/urls.py

from django.contrib import admin
from django.urls import path
from articles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
]
```

- `from articles import views` — articles 패키지에서 views 모듈을 가져오는 것
- `http://127.0.0.1:8000/index/` 로 요청이 왔을 때 views 모듈의 view 함수 `index`를 호출

> **규칙** — url 경로는 **반드시 `/` (slash)로 끝나야 한다.**

### 2. View 작성 (p.121-123)

```python
# articles/views.py

from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["GET"])
def index(request):
    return JsonResponse({"message": "Hello, world!"})
```

Json 응답 객체를 반환하는 `index` view 함수 정의다.

- 모든 view 함수는 첫번째 인자로 `request` 요청 객체를 **필수적으로** 받는다.
- 매개변수 이름이 `request`가 아니어도 되지만 **그렇게 작성하지 않는다.**

**`@api_view()` 데코레이터**

- DRF view 함수에서는 **필수로 작성**되며, view 함수를 실행하기 전 HTTP 메서드를 확인한다.
- 기본적으로 **GET 메서드만 허용**되며, 다른 메서드 요청에 대해서는 **405 Method Not Allowed**를 응답한다.
- 인자로 DRF view 함수가 응답해야 하는 HTTP 메서드 목록을 작성한다.

**`JsonResponse`** — Django에 내장된 HTTP 응답 클래스. 첫번째 위치 인자로 JSON으로 변환 가능한 데이터를 받아와 응답 객체를 반환해준다. 필요시 http response의 응답 상태 코드를 설정하여 반환 가능하다.

> **가장 흔한 실수** — `@api_view()`를 빼먹으면 DRF view가 아니게 되고, 반대로 `@api_view(["GET"])`만 써놓고 POST 요청을 보내면 405가 뜬다. 405를 만나면 데코레이터의 메서드 목록부터 확인할 것.

### 여러 HTTP 메서드 처리 (p.124)

```python
from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["GET", "POST"])
def index(request):
    if request.method == "POST":
        return JsonResponse({"data": request.data})
    return JsonResponse({"message": "Hello, world!"})
```

- view 함수의 첫번째 인자는 `request`로, HttpRequest 객체를 받아 옵니다.
- HTTP 메소드, 요청 데이터, 사용자 정보 등 `request` 객체를 활용하여 요청 데이터를 처리하고 적절한 응답을 생성할 수 있습니다.

---

## Variable Routing

### 현재 URL 관리의 문제점 (p.126)

템플릿의 많은 부분이 중복되고 URL의 일부만 변경되는 상황이라면, 계속해서 비슷한 URL과 함수를 작성해 나가야 할까?

```python
urlpatterns = [
    path('articles/1/', ...),
    path('articles/2/', ...),
    path('articles/3/', ...),
    path('articles/4/', ...),
    path('articles/5/', ...),
    ...
]
```

### Variable Routing이란 (p.127-129)

**Variable Routing** = URL 일부에 **변수를 포함**시키는 것. 변수는 view 함수의 인자로 전달할 수 있다.

**작성법**

```python
<path_converter:variable_name>

path('articles/<int:num>/', views.detail)
path('hello/<str:name>/', views.greeting)
```

URL 변수의 타입을 지정할 수 있으며, `str`, `int` 등 **5가지 타입**을 지원한다.
참고: `https://docs.djangoproject.com/en/5.2/topics/http/urls/#path-converters`

### 실습 (p.130-131)

**(1/2) 문자열 변수 — `<str:name>`**

```python
# articles/urls.py
urlpatterns = [
    path('hello/<str:name>/', views.greeting),
]
```

```python
# articles/views.py
@api_view(["GET"])
def greeting(request, name):
    context = {
        "name": name,
    }
    return JsonResponse(context)
```

**(2/2) 정수 변수 — `<int:num>`**

```python
# articles/urls.py
urlpatterns = [
    path('articles/<int:num>/', views.detail),
]
```

```python
# articles/views.py
@api_view(["GET"])
def detail(request, num):
    context = {
        "num": num,
    }
    return JsonResponse(context)
```

> **연결고리** — `<str:name>`의 `name`과 view 함수의 매개변수 `name`은 **이름이 같아야** 한다. URL에서 잡은 변수가 그 이름 그대로 view 함수의 인자로 넘어가기 때문이다. 이름이 다르면 `TypeError`가 난다.

---

## App과 URL 분리

### App URL mapping이 필요한 이유 (p.133-134)

**App URL mapping** = 프로젝트와 각 앱이 URL을 나누어 관리를 편하게 하기 위함.

**앱이 여러 개일 때 발생할 수 있는 문제**

- view 함수 이름이 같거나 같은 패턴의 URL 주소를 사용하게 되는 경우
- 아래 코드와 같이 해결해 볼 수 있으나 더 좋은 방법이 필요

```python
from articles import views as articles_views
from pages import views as pages_views

urlpatterns = [
    path('pages/', pages_views.index),
    ...
]
```

> **결론** — "URL은 각자 app에서 관리하자"

### 구조 변화 (p.135-136)

```text
[기존 url 구조]
project
├── urls ──┬──▶ articles/views
requests ──┘  └──▶ pages/views

[변경된 url 구조]
project
├── urls ──┬──▶ articles/urls ──▶ articles/views
requests ──┘  └──▶ pages/urls    ──▶ pages/views
```

프로젝트의 `urls.py`는 "어느 앱으로 보낼지"만 결정하고, 세부 경로는 각 앱의 `urls.py`가 책임진다.

### include() (p.137-139)

**`include()`** = 프로젝트 내부 다른 앱들의 URL을 참조할 수 있도록 매핑하는 함수. **URL의 일치하는 부분까지 잘라내고, 남은 문자열 부분은 후속 처리를 위해 include된 URL로 전달**한다.

**변경 후 — 프로젝트의 `urls.py`**

```python
# firstpjt/urls.py

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('pages/', include('pages.urls')),
]
```

**앱의 `urls.py` (직접 생성해야 함)**

```python
# articles/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index),
    path('<int:num>/', views.detail),
    path('hello/<str:name>/', views.greeting),
]
```

```python
# pages/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index),
]
```

> **핵심 동작** — `articles/hello/홍길동/` 요청이 들어오면, 프로젝트 `urls.py`가 `articles/`까지 잘라내고 남은 `hello/홍길동/`을 `articles/urls.py`로 넘긴다. 그래서 앱의 `urls.py`에는 `articles/`를 **다시 쓰지 않는다.** 여기서 중복해서 쓰는 것이 가장 흔한 실수다.

---

## request 객체와 MTV 정리

### View 함수의 request 객체 (p.141-143)

**request 객체** = 클라이언트로부터 서버로 전달된 **모든 정보를 포함하는 객체**. Django의 `HttpRequest` 클래스를 기반으로 한다.

**주요 구성 요소**

| 속성 | 내용 |
|---|---|
| `request.method` | Request 메서드 |
| `request.path` | 요청 경로 |
| `request.GET` | GET 데이터 — URL 쿼리 스트링에 포함된 데이터 |
| `request.POST` | POST 데이터 — 폼 데이터를 통해 전달된 데이터 |
| `request.COOKIES` | 쿠키 데이터 — 클라이언트에 저장된 쿠키 |
| `request.session` | 세션 데이터 — 서버에 저장된 사용자 세션 데이터 |

**확인 코드**

```python
print("HTTP Method:", request.method)             # 요청 메서드 출력
print("Path:", request.path)                      # 요청 경로 출력
print("GET Data:", request.GET)                   # GET 데이터 출력
print("POST Data:", request.POST)                 # POST 데이터 출력
print("FILES Data:", request.FILES)               # 파일 데이터 출력
print("Cookies:", request.COOKIES)                # 쿠키 데이터 출력
print("Session Data:", request.session)           # 세션 데이터 출력
print("Headers:", request.headers)                # 헤더 데이터 출력
print("Full URL:", request.build_absolute_uri())  # 전체 URL 출력
```

> **쿠키 vs 세션** — 쿠키는 **클라이언트**에 저장, 세션은 **서버**에 저장. 어디에 저장되느냐가 구분점이다.

### MTV 디자인 패턴 최종 정리 (p.144-146)

| 구성 | 역할 |
|---|---|
| **Model** | 데이터와 관련된 로직을 관리. 응용프로그램의 데이터 구조를 정의하고 데이터베이스의 기록을 관리 |
| **Template** | 레이아웃과 화면을 처리. 화면상의 사용자 인터페이스 구조와 레이아웃을 정의 |
| **View** | Model & Template과 관련한 로직을 처리해서 응답을 반환. 클라이언트의 요청에 대해 처리를 분기하는 역할 |

**View의 동작 예시**

- 데이터가 필요하다면 model에 접근해서 데이터를 가져오고,
- 가져온 데이터를 template로 보내 화면을 구성하고,
- 구성된 화면을 응답으로 만들어 클라이언트에게 반환

**전체 흐름도**

```text
HTTP Request
     │
     ▼
   URLs  (urls.py)
     │  Forward request to appropriate view
     ▼
   View  (views.py) ◀── read/write data ──▶ Model (models.py)
     │  ▲
     │  └────────────────────────────────── Template (<filename>.html)
     ▼
HTTP Response (HTML)

※ URLs ~ View ~ Model ~ Template 전체가 Django가 담당하는 부분
```

### 왜 Django는 MTV라고 부를까 (p.147)

Django 공식 FAQ의 설명을 요약하면 이렇다.

장고는 MVC 프레임워크로 보이지만, 컨트롤러를 "뷰"라고 부르고 뷰를 "템플릿"이라고 한다. 장고 팀이 MVC를 해석하기로는, "뷰"는 사용자에게 보여지는 데이터들을 설명한다 — 데이터가 "어떻게" 보이는지가 아니라 "어떤" 데이터를 보여주는지로 볼 수 있다는 것이다. 따라서 장고에서 "뷰"는 특정 URL에 대한 파이썬 콜백 함수이고, 어떻게 보여줄지는 템플릿에 위임한다. 그렇다면 "컨트롤러"는? 장고의 경우 **프레임워크 자체**가 그 역할을 한다. 프레임워크가 URL 설정에 따라 요청을 적절한 뷰에게 전달하기 때문이다.

> 참고: `https://docs.djangoproject.com/ko/5.2/faq/general/#faq-mtv`

### render 함수 (p.148)

주어진 템플릿을 주어진 컨텍스트 데이터와 결합하고, 렌더링 된 텍스트와 함께 `HttpResponse` 응답 객체를 반환하는 함수다.

```python
render(request, template_name, context)
```

| 인자 | 설명 |
|---|---|
| 1. `request` | 응답을 생성하는 데 사용되는 요청 객체 |
| 2. `template_name` | 템플릿 이름의 경로 |
| 3. `context` | 템플릿에서 사용할 데이터 (딕셔너리 타입으로 작성) |

### 지금까지 나온 Django의 규칙 (p.149-150)

1. `urls.py`에서 각 url 경로는 반드시 `/`로 끝남
2. `views.py`에서 모든 view 함수는 첫번째 인자로 요청 객체를 받음 — 매개변수 이름은 반드시 `request`로 지정
3. Django는 정해진 경로에 있는 template 파일만 읽어올 수 있음 — `app폴더/templates/` 이후

**프레임워크의 규칙을 지켜야 하는 이유**

프레임워크를 사용할 때는 일정한 규칙을 따라야 하며, 이는 저마다의 설계 철학이나 목표를 반영하고 있다. 일관성 유지, 보안 강화, 유지보수성 향상, 최적화 등이 그 이유다. 프레임워크는 개발자에게 도움을 주는 도구와 환경을 제공하기 위해 규칙을 정해 놓은 것이며, 우리는 이를 잘 활용하여 특정 기능을 구현하는 방법을 표준화하고 개발 프로세스를 단순화할 수 있도록 해야 한다.

---

## 정리 체크리스트

- [ ] 클라이언트-서버 구조에서 request와 response가 각각 무엇인지 설명할 수 있다
- [ ] Frontend와 Backend의 담당 영역과 기술 스택을 구분할 수 있다
- [ ] 가상환경이 필요한 두 가지 시나리오(버전 충돌 / 패키지 충돌)를 말할 수 있다
- [ ] `venv` 생성 → 활성화 → Django 설치 → `requirements.txt` 생성 순서를 외워서 쓸 수 있다
- [ ] `venv` 폴더는 왜 git에 올리지 않는지, 대신 무엇을 올리는지 답할 수 있다
- [ ] MVC와 MTV의 명칭 대응 관계를 그릴 수 있다 (특히 Controller → View)
- [ ] Project와 App의 차이를 카페 예시로 설명할 수 있다
- [ ] 앱은 왜 "생성 후 등록" 순서여야 하는지 안다
- [ ] `settings.py`, `urls.py`, `models.py`, `views.py`가 각각 무엇을 하는지 말할 수 있다
- [ ] REST에서 자원을 사용하는 3가지 축(식별/행위/표현)을 나열할 수 있다
- [ ] URL의 6개 구성 요소를 예시 URL에서 짚어낼 수 있다
- [ ] Anchor(`#`)가 서버로 전송되지 않는다는 것을 안다
- [ ] GET/POST/PUT/DELETE의 역할과 상태 코드 5개 그룹을 구분할 수 있다
- [ ] `@api_view()`의 역할과, 없을 때/메서드가 안 맞을 때 무슨 일이 생기는지 안다
- [ ] Variable Routing에서 URL 변수명과 view 함수 매개변수명의 관계를 안다
- [ ] `include()`가 URL을 어떻게 잘라서 넘기는지 설명할 수 있다
- [ ] `request` 객체의 주요 속성 6가지를 나열할 수 있다
- [ ] MTV 전체 흐름도를 백지에 그릴 수 있다

## 복습 문제

1. MVC의 `Controller`는 MTV에서 무엇에 해당하는가? — <details><summary>답</summary><b>View</b>. MVC의 View는 MTV의 Template이 되고, Controller가 View가 된다. 명칭만 바뀐 것이지 구조는 동일하다.</details>

2. `python -m venv venv` 명령에서 앞뒤의 `venv`는 각각 무엇인가? — <details><summary>답</summary>앞은 실행할 <b>모듈 이름</b>, 뒤는 생성될 <b>가상환경 폴더 이름</b>이다. 폴더 이름은 다른 것으로 바꿀 수 있지만 관례상 `venv`를 쓴다.</details>

3. 팀원이 clone 받은 Django 프로젝트가 실행되지 않는다. 가장 먼저 확인할 것은? — <details><summary>답</summary>가상환경을 만들고 활성화한 뒤 <code>pip install -r requirements.txt</code>를 실행했는지. <code>venv</code> 폴더는 <code>.gitignore</code>로 공유되지 않으므로 각자 환경을 새로 만들어야 한다.</details>

4. `https://example.com/search/?q=django#result` 에서 서버로 **전송되지 않는** 부분은? — <details><summary>답</summary><code>#result</code> (Anchor / fragment identifier). 브라우저가 해당 지점으로 스크롤하는 용도로만 쓰인다.</details>

5. REST에서 자원을 사용하는 3가지 방법과 각각의 수단은? — <details><summary>답</summary>1) 자원의 <b>식별</b> — URI, 2) 자원의 <b>행위</b> — HTTP Methods, 3) 자원의 <b>표현</b> — JSON 데이터</details>

6. `@api_view(["GET"])`이 붙은 view에 POST 요청을 보내면? — <details><summary>답</summary><b>405 Method Not Allowed</b>가 응답된다. 허용할 메서드를 <code>@api_view(["GET", "POST"])</code>처럼 목록에 추가해야 한다.</details>

7. 다음 코드에서 에러가 나는 이유는?
   ```python
   # urls.py
   path('hello/<str:name>/', views.greeting)

   # views.py
   def greeting(request, username):
       ...
   ```
   — <details><summary>답</summary>URL에서 캡처한 변수명은 <code>name</code>인데 view 함수의 매개변수는 <code>username</code>이라 이름이 맞지 않는다. <code>TypeError</code>가 발생한다. 둘의 이름은 반드시 일치해야 한다.</details>

8. 프로젝트 `urls.py`에 `path('articles/', include('articles.urls'))`가 있을 때, `articles/urls.py`에는 `articles/1/`을 어떻게 써야 하는가? — <details><summary>답</summary><code>path('&lt;int:num&gt;/', views.detail)</code>. <code>include()</code>가 <code>articles/</code>까지 이미 잘라냈으므로 앱의 urls.py에서 다시 쓰면 안 된다.</details>

9. `request.GET`과 `request.POST`의 차이는? — <details><summary>답</summary><code>request.GET</code>은 URL 쿼리 스트링에 포함된 데이터, <code>request.POST</code>는 폼 데이터를 통해 전달된 데이터다.</details>

10. Django의 3대 규칙을 말하라. — <details><summary>답</summary>1) urls.py의 url 경로는 반드시 <code>/</code>로 끝남, 2) 모든 view 함수는 첫번째 인자로 요청 객체를 받고 이름은 <code>request</code>로 지정, 3) template 파일은 정해진 경로(<code>app폴더/templates/</code> 이후)에 있어야 읽힘</details>

---

## 정리 노트

- 이 노트는 표지·간지·"이어서.." 페이지(p.1-2, 4-5, 7, 14, 19-21, 24, 30, 45, 50-52, 58, 71-73, 87, 97, 102, 108-110, 114, 125, 132, 140, 151)를 제외하고 작성했다.
- p.134의 `urlpatterns` 예시는 원본 슬라이드에서 코드 블록 일부가 잘려 있어, 판독 가능한 범위까지만 옮겼다. 개념(앱별 views를 alias로 import하는 임시 해결책) 전달에는 지장이 없다.
- OCR로 읽은 한글 본문 중 조사·어미가 깨진 부분은 문맥으로 복원했다. 코드·명령어·표의 값은 모두 이미지 또는 300dpi 영문 OCR 2회 교차검증으로 확인했다.
