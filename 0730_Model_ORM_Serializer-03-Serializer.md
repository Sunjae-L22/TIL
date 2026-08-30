# Model & ORM & Serializer — 03. Serializer

> 시리즈: [01 Model](0730_Model_ORM_Serializer-01-Model.md) · [02 ORM](0730_Model_ORM_Serializer-02-ORM.md) · **03 Serializer**
> 출처: `16기_데이터트랙_0730_Model_ORM_Serializer.pdf` (총 133페이지) · 정리일: 2026-07-30
> 페이지 표기는 PDF 기준 (슬라이드 인쇄 번호와 동일)

## 한눈에 보기

- Serialization(직렬화)이 정확히 무슨 과정을 가리키는가?
- `Serializer`와 `ModelSerializer`는 뭐가 다른가?
- `fields = '__all__'`과 `exclude`는 언제 다르게 써야 하는가?
- `model_to_dict`로 직접 딕셔너리를 만들던 예전 방식과 `ModelSerializer`는 뭐가 다른가?
- Create/Update에서 `is_valid()`는 왜 필요하고, `partial=True`는 언제 붙이는가?

## 목차

1. [Serialization 개요](#serialization-개요) (p.83-89)
2. [Serializer Class와 ModelSerializer](#serializer-class와-modelserializer) (p.90-95)
3. [ModelSerializer로 조회하기 — List / Detail](#modelserializer로-조회하기--list--detail) (p.96-107)
4. [ModelSerializer로 생성하기 — Create](#modelserializer로-생성하기--create) (p.108-116)
5. [ModelSerializer로 삭제하기 — Delete](#modelserializer로-삭제하기--delete) (p.117-119)
6. [ModelSerializer로 수정하기 — Update](#modelserializer로-수정하기--update) (p.120-124)
7. [부록](#부록) (p.125-133)

---

## Serialization 개요

### Serialization이란 (p.85, 88)

> **Serialization ("직렬화")**
> 여러 시스템에서 활용하기 위해, 데이터 구조나 객체 상태를 나중에 재구성할 수 있는 포맷으로 변환하는 과정. 어떠한 언어나 환경에서도 나중에 다시 쉽게 사용할 수 있는 데이터로 변환하는 과정이라고도 할 수 있다.

```text
객체(파이썬 객체/모델 인스턴스)  ── Serialization ──▶  Serialized data (예: JSON)
```

Python 환경에서만 쓸 수 있는 객체를, 어떤 언어·환경에서도 읽을 수 있는 공용 포맷(JSON 등)으로 바꿔주는 과정이 바로 Serialization이다. (p.86-89)

> Django 프로젝트에서는 이 변환 과정을 **Serializer Class**가 담당한다.

<br>

---

## Serializer Class와 ModelSerializer

### Serializer (p.91)

> **Serializer**
> Serialization을 진행하여 Serialized data를 반환해주는 클래스.

### ModelSerializer (p.92)

> **ModelSerializer**
> Django 모델과 연결된 Serializer 클래스. 일반 `Serializer`와 달리, 사용자 입력 데이터를 받아 **자동으로 모델 필드에 맞춰** Serialization을 진행한다.

### ModelSerializer class 작성 예시 (p.93)

`Article` 모델을 토대로 직렬화를 수행하는 `ArticleSerializer`를 정의한다.

```python
# articles/serializers.py
from rest_framework import serializers
from .models import Article

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
```

> `serializers.py`의 위치나 파일명 자체는 자유롭게 정할 수 있다. (관례적으로 앱 폴더 아래 `serializers.py`를 쓴다.)

### Meta class (p.94)

> **Meta class**
> `ModelSerializer`의 정보(어떤 모델을 대상으로 하는지, 어떤 필드를 포함할지 등)를 작성하는 곳.

### `fields`와 `exclude` 속성 (p.95)

`fields = '__all__'` 대신, 필요한 필드만 지정하거나 반대로 제외할 필드만 지정할 수도 있다.

```python
# 포함할 필드만 지정
class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title',)

# 제외할 필드만 지정
class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ('created_at', 'updated_at',)
```

> ✅ `fields`는 "이것만 보여준다"이고, `exclude`는 "이것만 빼고 다 보여준다"이다. 목록(List) 화면처럼 일부 필드만 필요할 때 `exclude`나 `fields`로 응답 크기를 줄일 수 있다.

<br>

---

## ModelSerializer로 조회하기 — List / Detail

### 리스트 조회 로직 (p.99-101)

**① Serializer** — 목록 조회에서는 `created_at`, `updated_at`을 뺀 간략한 정보만 보여준다.

```python
# articles/serializers.py
from rest_framework import serializers
from .models import Article

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ('created_at', 'updated_at',)
```

**② URL과 View**

```python
# articles/urls.py
urlpatterns = [
    path('', views.article_list),
]
```

```python
# articles/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleListSerializer

@api_view(['GET'])
def article_list(request):
    articles = Article.objects.all()
    serializer = ArticleListSerializer(articles, many=True)
    return Response(serializer.data)
```

**③ 응답 확인** — `GET http://127.0.0.1:8000/articles/`로 요청하면 `title`, `id`, `content`가 담긴 게시글 목록이 JSON 배열로 응답된다.

### ModelSerializer의 인자와 속성 (p.102)

```python
serializer = ArticleListSerializer(articles, many=True)
return Response(serializer.data)
```

| 인자/속성 | 의미 |
|---|---|
| `many` 옵션 | Serialize 대상이 여러 개(iterable, 예: QuerySet)인 경우 입력한다 |
| `.data` | Serialized data 객체에서 실제 데이터를 추출한다 |

### 과거 view 함수와의 비교 (p.103-104)

**과거 — `model_to_dict`로 직접 변환**

```python
@api_view(['GET'])
def article_list(request):
    articles = Article.objects.all()
    data = [model_to_dict(article) for article in articles]
    return JsonResponse({'data': data})

def model_to_dict(article):
    return {
        'id': article.id,
        'title': article.title,
        'content': article.content,
    }
```

QuerySet 객체에서 필요한 값만 직접 꺼내 딕셔너리 형태로 반환하던 방식이다. 필드가 하나 늘어날 때마다 `model_to_dict` 함수도 손으로 고쳐야 한다.

**현재 — `ModelSerializer` 사용**

```python
@api_view(['GET'])
def article_list(request):
    articles = Article.objects.all()
    serializer = ArticleListSerializer(articles, many=True)
    return Response(serializer.data)
```

JSON 데이터로 serialization하여 응답하는 현재의 view 함수는, 어떤 필드를 어떻게 내보낼지를 **Serializer 쪽에 위임**한다. view 함수는 조회하고 넘겨주는 역할만 한다.

> ✅ **핵심 차이** — `model_to_dict`는 필드를 하나하나 수동으로 꺼내야 하지만, `ModelSerializer`는 `Meta.fields`/`exclude` 설정만으로 자동 변환된다.

### 단일 조회 로직 (p.105-107)

**① Serializer** — 상세 조회에서는 모든 필드(작성일·수정일 포함)를 보여준다.

```python
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
```

**② URL과 View**

```python
# articles/urls.py
urlpatterns = [
    path('<int:article_pk>/', views.article_detail),
]
```

```python
from .serializers import ArticleSerializer

@api_view(['GET'])
def article_detail(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    serializer = ArticleSerializer(article)
    return Response(serializer.data)
```

> ⚠️ 단일 객체를 Serializer에 넘길 때는 `many=True`를 쓰지 않는다. 단일 조회는 QuerySet이 아니라 모델 인스턴스 하나를 반환하기 때문이다 (02-ORM 참고).

**③ 응답 확인** — `GET http://127.0.0.1:8000/articles/1/`로 요청하면 `id`, `title`, `content`, `created_at`, `updated_at`이 모두 담긴 단일 객체가 응답된다.

<br>

---

## ModelSerializer로 생성하기 — Create

### 응답 규칙 (p.109)

1. 데이터 생성이 성공했을 경우 **201 Created** 응답
2. 데이터 생성이 실패했을 경우 **400 Bad Request** 응답

### method별 분기 처리 (p.110)

`article_list` view 함수를 GET/POST 요청에 따라 분기하도록 구조를 바꾼다.

```python
from rest_framework import status

@api_view(['GET', 'POST'])
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

`POST http://127.0.0.1:8000/articles/`로 `title`, `content`를 담아 요청하면 `201 Created`와 함께 생성된 게시글(작성일 포함)이 응답된다. (p.111-112)

### `is_valid()`와 유효성 검사 (p.113-116)

> **`is_valid()`**
> 여러 유효성 검사를 실행하고, 데이터가 유효한지 여부를 Boolean으로 반환한다.

> **유효성 검사**
> 수집한 데이터가 정확하고 유효한지 확인하는 과정.

유효성 검사를 구현하려면 입력 값, 형식, 중복, 범위, 보안 등 많은 것들을 고려해야 한다. 이 과정을 직접 개발하는 대신, **DRF가 제공하는 Serializer class**를 사용한다.

예를 들어 필수 필드인 `content`를 빼고 요청을 보내면, `is_valid()`가 실패하며 `400 Bad Request`와 함께 아래와 같은 오류가 응답된다.

```json
{
    "content": [
        "This field is required."
    ]
}
```

> ✅ `is_valid()`를 거치지 않고 곧바로 `save()`를 호출하면 안 된다. **반드시 `is_valid()`로 검증한 뒤에만 저장**해야, 잘못된 데이터가 DB에 들어가는 것을 막을 수 있다.

<br>

---

## ModelSerializer로 삭제하기 — Delete

### 응답 규칙과 구현 (p.118)

요청에 대한 데이터 삭제가 성공했을 경우는 **204 No Content** 응답이다.

```python
@api_view(['GET', 'DELETE'])
def article_detail(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

`DELETE http://127.0.0.1:8000/articles/1/`로 요청하면 본문 없이 `204 No Content`가 응답된다. (p.119)

<br>

---

## ModelSerializer로 수정하기 — Update

### 응답 규칙과 구현 (p.121)

요청에 대한 데이터 수정이 성공했을 경우는 **200 OK** 응답이다.

```python
@api_view(['GET', 'DELETE', 'PUT'])
def article_detail(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    # ... GET, DELETE 분기 생략 ...
    elif request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

`PUT http://127.0.0.1:8000/articles/5/`로 수정할 `title`, `content`를 담아 요청하면 `200 OK`와 함께 수정된 데이터가 응답된다. 이어서 같은 대상을 `GET`으로 다시 조회하면 수정된 값이 그대로 반영되어 있다. (p.122-123)

### `partial` 인자 (p.124)

> **`partial` 인자**
> 부분 업데이트를 허용하기 위한 인자.

`partial` 값이 `False`(기본값)일 경우, 게시글 제목(`title`)만 수정하려고 해도 **반드시 `content` 값도 함께 요청에 담아 보내야** 한다. 기본적으로 serializer는 모든 필수 필드에 대한 값을 전달받기 때문이다. 즉, 수정하지 않는 다른 필드 데이터도 모두 함께 전송해야 하며, 그렇지 않으면 유효성 검사에서 오류가 발생한다.

```python
serializer = ArticleSerializer(article, data=request.data, partial=True)
```

> ✅ **일부 필드만 골라 수정하고 싶다면 `partial=True`를 반드시 추가한다.** PUT으로 전체 필드를 요구하는 대신, PATCH 요청 처리에 흔히 이 옵션을 사용한다.

<br>

---

## 부록

### 데이터베이스 초기화 (p.126)

1. migration 파일 삭제
2. `db.sqlite3` 파일 삭제

> ⚠️ 아래 파일과 폴더는 지우지 않도록 주의한다.
> - `migrations` 폴더 자체 (폴더 안의 migration 파일들만 삭제)
> - `__init__.py`

### Migrations 기타 명령어 (p.127)

```bash
$ python manage.py showmigrations
```

migration 파일들이 실제로 `migrate` 됐는지 안 됐는지 여부를 확인하는 명령어. `[X]` 표시가 있으면 migrate가 완료되었음을 의미한다.

```bash
$ python manage.py sqlmigrate articles 0001
```

해당 migration 파일이 SQL 언어로 어떻게 번역되어 DB에 전달되는지 확인하는 명령어.

### SQLite (p.129)

> **SQLite**
> 데이터베이스 관리 시스템 중 하나이며, Django의 기본 데이터베이스로 사용된다. 파일로 존재하며 이식 호환성이 좋다.

### QuerySet API를 사용하는 이유 (p.130)

- 데이터베이스 쿼리를 추상화하여, Django 개발자가 데이터베이스와 **직접 상호작용하지 않아도** 되도록 한다.
- 데이터베이스와의 결합도를 낮추고, 개발자가 더 직관적이고 생산적으로 개발할 수 있도록 돕는다.

### `raise_exception` (p.132)

> **`raise_exception`**
> `is_valid()`의 선택 인자. 유효성 검사를 통과하지 못했을 시 `ValidationError` 예외를 발생시킨다. DRF에서 제공하는 기본 예외 처리기에 의해 자동으로 처리되며, 기본적으로 HTTP **400** 응답을 반환한다.

```python
@api_view(['GET', 'POST'])
def article_list(request):
    # ... GET 분기 생략 ...
    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
```

`if serializer.is_valid(): ... return Response(serializer.errors, ...)`로 매번 실패 응답을 직접 작성하던 코드를, `raise_exception=True` 한 줄로 대체할 수 있다.

### 참고 문서 (p.131)

- https://docs.djangoproject.com/en/5.2/ref/models/querysets/
- https://docs.djangoproject.com/en/5.2/topics/db/queries/

<br>

---

## 정리 체크리스트

- [ ] Serialization이 무엇을 무엇으로 바꾸는 과정인지 설명할 수 있다
- [ ] `Serializer`와 `ModelSerializer`의 차이를 설명할 수 있다
- [ ] `Meta` class에서 `fields`와 `exclude`를 구분해서 쓸 수 있다
- [ ] `model_to_dict` 방식과 `ModelSerializer` 방식의 차이를 설명할 수 있다
- [ ] Create/Update에서 `is_valid()`를 반드시 거쳐야 하는 이유를 설명할 수 있다
- [ ] CRUD 각 동작이 성공했을 때 반환하는 상태 코드(200/201/204)를 구분할 수 있다
- [ ] `partial=True`가 왜 필요한지 설명할 수 있다

## 복습 문제

1. 목록 조회용 Serializer에서 `exclude = ('created_at', 'updated_at',)`로 설정한 이유는 무엇이라고 생각하는가? <details><summary>답</summary>목록 화면에서는 게시글의 작성일·수정일까지는 필요 없는 경우가 많아, 불필요한 필드를 빼서 응답 데이터 크기를 줄이기 위함이다. 상세 조회용 Serializer(`ArticleSerializer`)는 `fields = '__all__'`로 모든 필드를 포함한다.</details>
2. `model_to_dict`로 직접 딕셔너리를 만들던 방식과 비교했을 때, `ModelSerializer`를 쓰면 무엇이 줄어드는가? <details><summary>답</summary>필드가 추가/삭제될 때마다 직접 수정해야 했던 변환 함수(`model_to_dict`)가 필요 없어진다. `Meta.fields`/`exclude` 설정만 바꾸면 되므로, view 함수는 조회와 응답 역할에만 집중할 수 있다.</details>
3. `serializer.is_valid()`를 호출하지 않고 바로 `serializer.save()`를 호출하면 어떤 문제가 생길 수 있는가? <details><summary>답</summary>입력 값, 형식, 필수 필드 누락 등 유효성 검사를 거치지 않은 상태이므로, 잘못되거나 불완전한 데이터가 그대로 DB에 저장될 수 있다.</details>
4. 게시글의 `title`만 수정하고 싶은데 `content`는 요청에 담지 않았다. `partial` 옵션 없이 `PUT`을 보내면 어떻게 되는가? <details><summary>답</summary>`partial`이 기본값(False)이면 serializer는 모든 필수 필드의 값을 요구하므로, `content`가 빠진 요청은 유효성 검사에서 오류가 발생한다. `partial=True`를 추가해야 일부 필드만으로도 수정이 가능하다.</details>
