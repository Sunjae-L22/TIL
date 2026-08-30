# Model & ORM & Serializer — 02. ORM

> 시리즈: [01 Model](0730_Model_ORM_Serializer-01-Model.md) · **02 ORM** · [03 Serializer](0730_Model_ORM_Serializer-03-Serializer.md)
> 출처: `16기_데이터트랙_0730_Model_ORM_Serializer.pdf` (총 133페이지) · 정리일: 2026-07-30
> 페이지 표기는 PDF 기준 (슬라이드 인쇄 번호와 동일)

## 한눈에 보기

- ORM은 정확히 어떤 문제를 해결해 주는가?
- `Article.objects.all()`에서 `.objects`와 `QuerySet`은 각각 무엇인가?
- 데이터를 새로 만드는 세 가지 방법은 서로 뭐가 다른가?
- `get()`을 `filter()` 대신 쓰면 안 되는 상황은 언제인가?
- CRUD 각 동작(Create/Read/Update/Delete)의 최소 코드 패턴은 무엇인가?

## 목차

1. [ORM 개요](#orm-개요) (p.42-46)
2. [QuerySet API 개념](#queryset-api-개념) (p.47-56)
3. [실습 준비 — Postman과 skeleton 프로젝트](#실습-준비--postman과-skeleton-프로젝트) (p.56-64)
4. [CRUD 실습 — Create](#crud-실습--create) (p.65-71)
5. [CRUD 실습 — Read](#crud-실습--read) (p.72-77)
6. [CRUD 실습 — Update](#crud-실습--update) (p.78-79)
7. [CRUD 실습 — Delete](#crud-실습--delete) (p.80-81)

---

## ORM 개요

### ORM이 해결하는 문제 (p.44-46)

> **Object-Relational-Mapping (ORM)**
> 객체 지향 프로그래밍 언어를 사용하여, 호환되지 않는 유형의 시스템 간에 데이터를 변환하는 기술.

Python과 데이터베이스는 애초에 사용하는 언어(자료구조)가 다르기 때문에, 둘을 직접 이어 붙이면 서로 소통할 수 없다.

```text
Python  ─────────✕─────────  Database      (사용하는 언어가 달라 직접 소통 불가)
```

Django에 내장된 ORM이 그 사이에서 통역을 담당한다.

```text
Python  ───────  ORM  ───────  Database      (ORM이 중간에서 서로의 언어를 해석)
```

즉 개발자는 Python 코드(객체 지향 문법)만 다루면 되고, 그 코드를 실제 SQL로 바꾸는 일은 ORM이 대신한다.

<br>

---

## QuerySet API 개념

### QuerySet API란 (p.48, 54)

ORM이 데이터를 **검색, 필터링, 정렬, 그룹화**하는 데 사용하는 도구다. API를 사용하여 SQL이 아닌 **Python 코드로 데이터를 처리**한다.

> **QuerySet API**
> Python의 모델 클래스와 인스턴스를 활용해 DB의 데이터를 저장·조회·수정·삭제하는 것.

### 동작 구조 (p.49-51)

```text
Article.objects.all()
   │        │      │
   │        │      └─ QuerySet API — 실제 동작(조회 등)을 수행
   │        └──────── Manager — 모델과 DB를 이어주는 관리자
   └───────────────── Model class
```

`Article.objects.all()`을 호출하면, Python 코드가 ORM을 거쳐 SQL로 변환되어 데이터베이스에 전달되고, 데이터베이스는 그 결과를 다시 ORM을 거쳐 Python이 다룰 수 있는 형태로 돌려준다.

```text
Python(Article.objects.all())  ──▶  ORM  ──▶  Database
Python(QuerySet 결과 받음)      ◀──  ORM  ◀──  Database
```

### Query와 QuerySet (p.52-53)

> **Query**
> 데이터베이스에 특정한 데이터를 보여 달라는 요청. "쿼리문을 작성한다"는 말은, 원하는 데이터를 얻기 위해 데이터베이스에 요청을 보낼 코드를 작성한다는 뜻이다.
>
> 파이썬으로 작성한 코드가 ORM에 의해 SQL로 변환되어 데이터베이스에 전달되며, 데이터베이스의 응답 데이터를 ORM이 **QuerySet**이라는 자료 형태로 변환하여 우리에게 전달한다.

> **QuerySet**
> 데이터베이스에게서 전달받은 객체 목록(데이터 모음). 순회가 가능한 데이터로써 1개 이상의 데이터를 불러와 사용할 수 있다. Django ORM을 통해 만들어진 자료형이다.

> ⚠️ **단일 객체를 반환할 때는 QuerySet이 아니다.** 데이터베이스가 단일한 객체를 반환할 때는 QuerySet이 아닌, **모델(Model)의 인스턴스**로 반환된다. (예: `objects.all()` → QuerySet / `objects.get()` → 모델 인스턴스 하나)

<br>

---

## 실습 준비 — Postman과 skeleton 프로젝트

### Postman (p.57-60)

> **Postman**
> API를 구축하고 사용하기 위한 플랫폼. API를 빠르게 만들고 테스트할 수 있는 여러 도구 및 기능을 제공한다. (https://www.postman.com/downloads/)

이후 실습에서는 CRUD 각 기능을 아래와 같은 HTTP method + URL 조합으로 설계해 Postman으로 요청을 보내며 확인한다.

| 기능 | Method | URL |
|---|---|---|
| 목록 조회 | `GET` | `/articles/` |
| 게시글 생성 | `POST` | `/articles/` |
| 상세 조회 | `GET` | `/articles/<pk>/` |
| 게시글 수정 | `PUT` | `/articles/<pk>/` |
| 게시글 삭제 | `DELETE` | `/articles/<pk>/` |

> 📌 원본 슬라이드(p.60)의 URL·method 설계표는 이미지 인식이 되지 않아, 이후 실습(p.101, 107, 111, 119, 122)에서 실제로 사용된 요청 URL을 근거로 표를 재구성했다. 표의 형태(기능 → method/URL 대응)는 원본과 동일하되, 정확한 원문 문구까지는 보장하지 않는다.

### skeleton 프로젝트 안내 (p.61)

1. 가상 환경 생성, 활성화 및 패키지 설치 — 외부 패키지 및 라이브러리는 `requirements.txt`에 작성되어 있음

   ```bash
   $ python -m venv venv
   $ source venv/Scripts/activate
   $ pip install -r requirements.txt
   ```

2. migrate 진행

   ```bash
   $ python manage.py makemigrations
   $ python manage.py migrate
   ```

3. 프로젝트는 **"주석을 해제"** 하며 진행

### Skeleton code 살펴보기 (p.62-64)

**① `config/urls.py`** — `articles` 앱을 QuerySet API 실습에 사용한다.

```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
]
```

**② `articles/urls.py`** — 이후 CRUD 실습에서 뷰가 하나씩 채워진다.

**③ `Article` 모델 클래스** — `__str__`이 추가되어, admin이나 shell에서 객체를 출력할 때 `title`이 보이도록 했다.

```python
# articles/models.py
class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title
```

<br>

---

## CRUD 실습 — Create

### 데이터 객체를 만드는 3가지 방법 (p.66-70)

**첫번째 방법 — 인스턴스를 만들고 속성을 하나씩 대입** (p.66-68)

```python
@api_view(['POST'])
def article_create(request):
    article = Article()  # Article 클래스의 인스턴스 생성
    article.title = request.data.get('title')
    article.content = request.data.get('content')
    article.save()  # 이 시점에 비로소 데이터베이스에 저장됨
    return JsonResponse({'id': article.id}, status=status.HTTP_201_CREATED)
```

**두번째 방법 — 인스턴스 생성과 동시에 값을 대입** (p.69)

```python
article = Article(title=request.data.get('title'), content=request.data.get('content'))
article.save()
```

`save()` 메서드를 호출해야 비로소 DB에 데이터가 저장된다. 테이블에 한 줄(행, 레코드)이 쓰여지는 것이다.

**세번째 방법 — QuerySet API의 `create()` 메서드 활용** (p.70)

```python
article = Article.objects.create(
    title=request.data.get('title'),
    content=request.data.get('content'),
)
```

> `create()`는 인스턴스 생성과 `save()` 호출을 한 번에 처리해 주는 축약형이다.

> ✅ **`save()`**
> 객체를 데이터베이스에 저장하는 메서드. 세 가지 방법 모두 결국 `save()`(또는 이를 내부적으로 호출하는 `create()`)가 실행되어야 실제로 DB에 반영된다. (p.71)

<br>

---

## CRUD 실습 — Read

### 주요 조회 메서드 (p.73)

| 구분 | 메서드 |
|---|---|
| 새로운 QuerySet을 반환 | `all()`, `filter()` |
| QuerySet을 반환하지 않음 | `get()` |

### 전체 데이터 조회 — `all()` (p.74)

```python
Article.objects.all()
# <QuerySet [<Article: Article object (1)>, <Article: Article object (2)>, <Article: Article object (3)>]>
```

### 조건 조회 — `filter()` (p.75)

```python
articles = Article.objects.filter(title='title')
# <QuerySet [<Article: Article object (1)>, <Article: Article object (2)>]>

articles = Article.objects.filter(title='django')
# <QuerySet []>   ← 조건에 맞는 데이터가 없으면 빈 QuerySet

articles = Article.objects.filter(title='article_02')
# <QuerySet [<Article: Article object (1)>]>
```

### 단일 데이터 조회 — `get()` (p.76-77)

```python
article = Article.objects.get(pk=1)
# <Article: Article object (1)>

article = Article.objects.get(pk=100)
# DoesNotExist: Article matching query does not exist.

article = Article.objects.get(title='title')
# MultipleObjectsReturned: get() returned more than one Article -- it returned 2!
```

> ⚠️ **`get()`의 특징과 주의할 점**
> 조건에 맞는 데이터를 찾을 수 없으면 `DoesNotExist` 예외를, 둘 이상의 객체를 찾으면 `MultipleObjectsReturned` 예외를 발생시킨다. 이런 특징이 있기 때문에 `get()`은 **primary key처럼 고유성(uniqueness)이 보장되는 조회**에서 사용해야 한다. 여러 개가 나올 수 있는 조건에는 `filter()`를 쓴다.

<br>

---

## CRUD 실습 — Update

### 데이터 수정 (p.79)

인스턴스의 변수를 변경한 뒤 `save()` 메서드를 다시 호출하면 수정이 반영된다.

```python
@api_view(['PUT'])
def article_update(request, pk):
    article = Article.objects.get(pk=pk)
    article.title = request.data.get('title')
    article.content = request.data.get('content')
    article.save()  # 변경된 내용을 데이터베이스에 저장
    return JsonResponse(model_to_dict(article))
```

> ✅ 생성과 수정 모두 결국 **"객체를 가져오거나 만들고 → 값을 바꾸고 → `save()`를 호출"** 하는 동일한 흐름을 따른다.

<br>

---

## CRUD 실습 — Delete

### 데이터 삭제 (p.81)

삭제하려는 데이터를 조회한 뒤 `delete()` 메서드를 호출한다.

```python
@api_view(['DELETE'])
def article_delete(request, pk):
    article = Article.objects.get(pk=pk)
    article.delete()
```

<br>

---

## 정리 체크리스트

- [ ] ORM이 Python과 데이터베이스 사이에서 하는 역할을 설명할 수 있다
- [ ] `Article.objects.all()`에서 Manager와 QuerySet API의 위치를 구분할 수 있다
- [ ] QuerySet과 모델 인스턴스가 각각 언제 반환되는지 설명할 수 있다
- [ ] 데이터를 생성하는 세 가지 방법을 코드로 쓸 수 있다
- [ ] `get()`을 `filter()` 대신 함부로 쓰면 안 되는 이유를 설명할 수 있다
- [ ] Update와 Delete의 최소 코드 패턴을 쓸 수 있다

## 복습 문제

1. `Article.objects.filter(title='없는제목')`처럼 조건에 맞는 데이터가 하나도 없을 때, `filter()`와 `get()`은 각각 어떻게 반응하는가? <details><summary>답</summary>`filter()`는 빈 QuerySet(`<QuerySet []>`)을 반환하며 에러가 나지 않는다. 반면 `get()`은 데이터를 찾지 못하면 `DoesNotExist` 예외를 발생시킨다.</details>
2. 데이터를 새로 만드는 세 가지 방법의 공통점은 무엇인가? <details><summary>답</summary>어떤 방법을 쓰든 결국 `save()` 메서드가 호출되어야 실제로 데이터베이스에 저장된다. 세번째 방법(`objects.create()`)은 인스턴스 생성과 `save()` 호출을 한 번에 묶어 처리하는 축약형일 뿐이다.</details>
3. `get()`을 primary key가 아닌, 값이 중복될 수 있는 필드(예: `title`) 조건으로 사용하면 어떤 문제가 생길 수 있는가? <details><summary>답</summary>조건에 맞는 객체가 둘 이상이면 `MultipleObjectsReturned` 예외가 발생한다. `get()`은 결과가 정확히 하나임을 보장하는 고유한 조건(primary key 등)에만 사용해야 한다.</details>
