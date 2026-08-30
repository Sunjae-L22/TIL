# Model & ORM & Serializer — 01. Model

> 시리즈: **01 Model** · [02 ORM](0730_Model_ORM_Serializer-02-ORM.md) · [03 Serializer](0730_Model_ORM_Serializer-03-Serializer.md)
> 출처: `16기_데이터트랙_0730_Model_ORM_Serializer.pdf` (총 133페이지) · 정리일: 2026-07-30
> 페이지 표기는 PDF 기준 (슬라이드 인쇄 번호와 동일)

## 한눈에 보기

- Model 클래스는 왜 "테이블 설계도"라고 부르는가?
- `makemigrations`와 `migrate`는 각각 무슨 일을 하고, 왜 항상 세트로 실행해야 하는가?
- 이미 데이터가 쌓인 테이블에 필드를 새로 추가하면 왜 기본값을 입력해야 하는가?
- `CharField`, `TextField`, `DateTimeField`는 언제 구분해서 써야 하는가?
- Django Admin은 왜 코드를 거의 안 짜도 관리자 화면이 생기는가?

## 목차

1. [Model 기초](#model-기초) (p.4-14)
2. [Migrations](#migrations) (p.15-27)
3. [Model Field 종류](#model-field-종류) (p.28-34)
4. [Admin site](#admin-site) (p.34-41)

---

## Model 기초

### Model이 하는 일 (p.5-6)

Django 프로젝트에서 데이터가 오가는 경로는 다음과 같다.

```text
urls.py → views.py ↔ models.py ↔ Database
                  ↕
              templates
```

`views.py`가 `models.py`를 통해 데이터베이스와 주고받는다. 이 흐름에서 **Model**이 맡는 역할은 이렇게 정의된다.

> **Django Model**
> DB의 테이블을 정의하고 데이터를 조작할 수 있는 기능들을 제공한다. 테이블 구조를 설계하는 **"청사진(blueprint)"** 이다.

### model 클래스 작성 (p.7)

```python
# articles/models.py
class Article(models.Model):
    title = models.CharField(max_length=10)
    content = models.TextField()
```

### model 클래스 살펴보기 (p.8-12)

이 짧은 클래스 하나가 실제로 하는 일을 다섯 단계로 뜯어보면 다음과 같다.

**① 테이블 구조로 변환된다 (p.8)**

작성한 모델 클래스는 최종적으로 DB에 아래와 같은 테이블 구조를 만든다.

| id | title | content |
|---|---|---|

`id` 필드는 Django가 자동으로 생성해 준다. **"모델 클래스 == 테이블 설계도"** 라는 말이 여기서 나온다.

**② `models.Model`을 상속받는다 (p.9)**

`class Article(models.Model)`에서 `Article`은 `django.db.models` 모듈의 `Model`이라는 부모 클래스를 상속받는다. `Model`은 모델에 관련된 모든 코드가 이미 작성되어 있는 클래스다.

> 개발자는 가장 중요한 **테이블 구조를 어떻게 설계할지에 대한 코드만** 작성하도록 하기 위한 설계다. 상속을 활용해 프레임워크가 나머지 기능을 대신 제공하는 방식이다.

**③ 클래스 변수명 = 필드(열) 이름 (p.10)**

`title`, `content`처럼 클래스 안에 선언한 변수명이 그대로 테이블의 **필드(열) 이름**이 된다.

**④ model Field 클래스 = 데이터 타입 (p.11)**

`CharField()`, `TextField()`처럼 오른쪽에 오는 클래스가 그 필드에 저장되는 **데이터 타입**을 결정한다.

**⑤ Field 클래스의 키워드 인자(필드 옵션) = 제약조건 (p.12)**

`CharField(max_length=10)`에서 `max_length=10`처럼 Field 클래스에 넘기는 키워드 인자를 **필드 옵션**이라고 부르며, 테이블 필드의 **제약조건**을 설정한다.

> 📌 원본 슬라이드는 이 다섯 단계를 "model 클래스 살펴보기 (1/5)~(5/5)"로 한 장씩 나눠 보여준다. 노트에서는 하나로 묶었다.

### 제약 조건 (p.13)

> **제약 조건**
> 데이터가 올바르게 저장되고 관리되도록 하기 위한 규칙.
> 예) 숫자만 저장되도록, 문자가 100자까지만 저장되도록 하는 등.

<br>

---

## Migrations

### Migrations란 (p.16)

> **Migrations**
> model 클래스의 변경사항(필드 생성, 수정, 삭제 등)을 DB에 최종 반영하는 방법.

### Migrations 과정 (p.17-19)

```text
model class          makemigrations         migration 파일           migrate          db.sqlite3
(설계도 초안)   ────────────────▶   (최종 설계도, 0001_initial.py)  ────────────▶     (DB)
```

핵심 명령어는 두 가지뿐이다.

```bash
$ python manage.py makemigrations
```

model class를 기반으로 최종 설계도(migration 파일)를 작성한다.

```bash
$ python manage.py migrate
```

최종 설계도를 DB에 전달하여 반영한다.

`migrate` 이후 `Article` 모델 클래스로 만들어진 `articles_article` 테이블이 DB 안에 실제로 생성된다 (컬럼: `id INTEGER`, `title varchar(10)`, `content TEXT`).

> ✅ **`makemigrations`는 설계도만 만들고, `migrate`가 실제로 DB에 반영한다.** 이 두 단계는 항상 세트다.

### 이미 생성된 테이블에 필드를 추가한다면 (p.21-27)

이미 데이터가 있는 테이블에 `created_at`, `updated_at` 필드를 새로 추가하는 상황을 예로 든다.

```python
# articles/models.py
class Article(models.Model):
    title = models.CharField(max_length=10)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

이미 기존 테이블이 존재하기 때문에, 필드를 추가할 때는 **기존 행들을 채울 기본값**을 설정해야 한다. `makemigrations`를 실행하면 아래처럼 선택을 요구한다.

```text
$ python manage.py makemigrations
It is impossible to add the field 'created_at' with 'auto_now_add=True' to article
without providing a default. This is because the database needs something to populate
existing rows.
 1) Provide a one-off default now which will be set on all existing rows
 2) Quit and manually define a default value in models.py.
Select an option:
```

- **1번** — 현재 대화(프롬프트)를 유지하면서 직접 기본값을 입력하는 방법 (권장)
- **2번** — 대화에서 나간 뒤 `models.py`에 기본값 관련 설정을 직접 하는 방법

날짜 데이터이므로 직접 값을 입력하기보다 Django가 제안하는 기본값을 쓰는 편이 낫다. 아무것도 입력하지 않고 Enter를 누르면 Django가 제안하는 기본값으로 설정된다.

```text
Please enter the default value as valid Python.
Accept the default 'timezone.now' by pressing 'Enter' or provide another value.
The datetime and django.utils.timezone modules are available, so it is possible to
provide e.g. timezone.now as a value.
Type 'exit' to exit this prompt
[default: timezone.now] >>>
```

이 과정이 끝나면 두 번째 migration 파일이 생성된다.

```text
Migrations for 'articles':
  articles\migrations\0002_article_created_at_article_updated_at.py
    - Add field created_at to article
    - Add field updated_at to article
```

> 💡 Django는 이렇게 설계도를 계속 쌓아가면서, 추후 문제가 생기면 복구하거나 되돌릴 수 있도록 한다. **마치 `git commit`과 유사**한 개념이다.

마지막으로 `migrate`를 실행하면 테이블에 실제로 `created_at`, `updated_at` 컬럼이 추가된 것을 확인할 수 있다.

```bash
$ python manage.py migrate
```

> ✅ **정리 — model 변경의 3단계**
> model class에 변경사항이 생겼다면, 반드시 새로운 설계도를 생성하고, 이를 DB에 반영해야 한다.
> **1. model class 변경 → 2. `makemigrations` → 3. `migrate`**

<br>

---

## Model Field 종류

> **Model Field**
> DB 테이블의 필드(열)을 정의하며, 해당 필드에 저장되는 **데이터 타입**과 **제약조건**을 정의한다. (p.29)

지금까지 실습에 등장한 세 가지 Field 클래스는 다음과 같다.

| Field 클래스 | 용도 |
|---|---|
| `CharField()` | 길이의 제한이 있는 문자열을 넣을 때 사용. 필드의 최대 길이를 결정하는 `max_length`는 **필수 인자**다 (p.30) |
| `TextField()` | 길이 제한이 없는 긴 문자열(본문 등)을 넣을 때 사용 (p.31) |
| `DateTimeField()` | 날짜와 시간을 넣을 때 사용 (p.32) |

> ⚠️ `CharField`는 `max_length`를 반드시 지정해야 하지만, `TextField`는 길이를 제한하지 않는다. 짧고 정형화된 값(제목 등)은 `CharField`, 길이가 가변적인 본문·설명은 `TextField`로 구분해서 쓴다.

<br>

---

## Admin site

### Automatic admin interface (p.35)

Django는 추가 설치 및 설정 없이 **자동으로 관리자 인터페이스**를 제공한다. 데이터 확인 및 테스트를 진행하는 데 매우 유용하다.

### 4단계로 admin 화면 띄우기 (p.36-40)

**1. admin 계정 생성**

```bash
$ python manage.py createsuperuser
```

- email은 선택사항이므로 입력하지 않고 진행 가능
- 비밀번호 입력 시 보안상 터미널에 값이 출력되지 않으니, 그대로 무시하고 입력을 이어간다

**2. DB에 생성된 admin 계정 확인**

`auth_user` 테이블에 방금 만든 계정이 저장된 것을 SQL로 직접 조회해 확인할 수 있다 (`SELECT * FROM auth_user LIMIT 100`).

**3. admin에 모델 클래스 등록**

`admin.py`에 모델 클래스를 등록해야만 admin 사이트에서 확인할 수 있다.

```python
# articles/admin.py
from django.contrib import admin
from .models import Article

admin.site.register(Article)
```

**4. admin site 로그인 후 등록된 모델 확인**

로그인하면 `Site administration` 화면에 등록한 `Articles`가 `Groups`, `Users`와 함께 나타나고, 여기서 게시글 데이터를 직접 추가·수정할 수 있다.

> ✅ **admin 사이트는 "모델 클래스를 등록"해야만 보인다.** `admin.py`에 등록을 빠뜨리는 게 흔한 실수다.

<br>

---

## 정리 체크리스트

- [ ] 모델 클래스의 클래스 변수명 → 필드 이름, Field 클래스 → 데이터 타입, 키워드 인자 → 제약조건이라는 대응관계를 설명할 수 있다
- [ ] `makemigrations`와 `migrate`의 역할 차이를 설명할 수 있다
- [ ] 이미 데이터가 있는 테이블에 필드를 추가할 때 기본값이 왜 필요한지 설명할 수 있다
- [ ] `CharField`와 `TextField`의 차이를 말할 수 있다
- [ ] admin 사이트에서 모델을 확인하려면 어떤 파일에 무엇을 해야 하는지 말할 수 있다

## 복습 문제

1. `class Article(models.Model):`에서 `Article`이 상속받는 `Model` 클래스는 어떤 역할을 하는가? <details><summary>답</summary>django.db.models 모듈에 정의된 부모 클래스로, 모델에 관련된 모든 코드가 이미 작성되어 있다. 개발자는 테이블 구조 설계(필드 정의)만 신경 쓰면 되고, 나머지 기능은 상속을 통해 프레임워크가 제공한다.</details>
2. `makemigrations`만 실행하고 `migrate`를 실행하지 않으면 어떻게 되는가? <details><summary>답</summary>변경사항을 반영한 migration 파일(설계도)만 생성될 뿐, 실제 DB의 테이블 구조는 바뀌지 않는다. `migrate`까지 실행해야 최종 설계도가 DB에 전달되어 반영된다.</details>
3. 이미 데이터가 존재하는 테이블에 `auto_now_add=True`인 `DateTimeField`를 추가하려고 하면 왜 에러가 나는가? <details><summary>답</summary>기존에 저장된 행들에는 채워 넣을 값이 없기 때문에, 데이터베이스가 그 값을 무엇으로 채울지(기본값) 알아야 한다. Django는 이때 일회성 기본값을 입력할지, `models.py`에서 직접 기본값을 정의할지 선택하도록 요구한다.</details>
4. admin 사이트에 모델이 보이지 않는다면 가장 먼저 확인할 곳은? <details><summary>답</summary>`admin.py`에 `admin.site.register(모델명)`으로 해당 모델을 등록했는지 확인한다.</details>
