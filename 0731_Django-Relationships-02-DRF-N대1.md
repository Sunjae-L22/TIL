# DRF with N:1 — 댓글 CRUD와 응답 데이터 재구성

> 시리즈: [01 N:1 관계](0731_Django-Relationships-01-N대1관계.md) · **02 DRF with N:1** · [03 M:N 관계](0731_Django-Relationships-03-N대M관계.md) · [04 실습과 shortcuts](0731_Django-Relationships-04-실습과-shortcuts.md)

> 출처: `16기_데이터트랙_0731_Django_Relationships.pdf` (총 119페이지) · 정리일: 2026-07-31
> 페이지 표기는 PDF 기준

## 한눈에 보기

- N:1 관계가 걸린 모델의 CRUD API를 URL 설계부터 끝까지 만들 수 있는가
- 댓글 생성 시 `article` 필드 때문에 400이 나는 이유와 해결책
- `read_only_fields` **속성**과 `read_only` **인자**는 언제 갈리는가
- 게시글 응답에 댓글 목록·댓글 개수를 얹는 두 가지 방법
- `annotate`와 `SerializerMethodField`는 각각 어느 계층의 도구인가

## 목차

1. [사전 준비 — 모델과 URL 설계](#사전-준비--모델과-url-설계) (p.30-31)
2. [POST — 댓글 생성](#post--댓글-생성) (p.33-39)
3. [GET · DELETE · PUT — 나머지 CRUD](#get--delete--put--나머지-crud) (p.41-49)
4. [응답 데이터 재구성 — 중첩 Serializer](#응답-데이터-재구성--중첩-serializer) (p.51-56)
5. [역참조 데이터 구성 — 댓글 목록 붙이기](#역참조-데이터-구성--댓글-목록-붙이기) (p.59-62)
6. [댓글 개수 붙이기 — annotate](#댓글-개수-붙이기--annotate) (p.63-68)
7. [SerializerMethodField](#serializermethodfield) (p.69-75)

---

## 사전 준비 — 모델과 URL 설계

### Comment 모델 정의 (p.30)

1편과 거의 같지만 **`content`가 `CharField`에서 `TextField`로 바뀌었다.**

```python
# articles/models.py

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### URL 및 HTTP request method 구성 (p.31)

| URL | GET | POST | PUT | DELETE |
|---|---|---|---|---|
| `comments/` | 댓글 목록 조회 | | | |
| `comments/1/` | 단일 댓글 조회 | | 단일 댓글 수정 | 단일 댓글 삭제 |
| `articles/1/comments/` | | 댓글 생성 | | |

> **생성만 URL 모양이 다르다** — 조회·수정·삭제는 댓글 자신의 pk만 있으면 되지만, 생성은 **어느 게시글에 달 것인지**가 반드시 필요하다. 그 정보를 담을 곳이 URL밖에 없어서 `articles/<article_pk>/comments/` 형태가 된다. 이 비대칭이 뒤에 나올 400 에러의 출발점이다.

---

## POST — 댓글 생성

### CommentSerializer 정의 (p.33)

```python
# articles/serializers.py

from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
```

### url 및 view 함수 (p.34)

```python
# articles/urls.py

urlpatterns = [
    ...,
    path('<int:article_pk>/comments/', views.comment_create),
]
```

```python
# articles/views.py

@api_view(['POST'])
def comment_create(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

여기서 `article` 변수를 조회해 놓고 **쓰지 않는다.** 다음 단계에서 쓰인다.

### `save()`에 추가 데이터 넘기기 (p.35)

> serializer 인스턴스의 `save()` 메서드는 특정 Serializer 인스턴스를 저장하는 과정에서 추가 데이터를 받을 수 있다.

```python
# articles/views.py

@api_view(['POST'])
def comment_create(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

`article`은 요청 본문이 아니라 **URL에서 온 값**이므로, 검증이 끝난 뒤 저장 시점에 직접 꽂아 넣는다.

### 400 Bad Request가 나는 이유 (p.36-37)

`content`만 담아 POST를 보내면 이런 응답이 온다.

```json
{
    "article": [
        "This field is required."
    ]
}
```

원인은 이렇다.

> `CommentSerializer`에서 외래 키에 해당하는 `article` 필드 또한 사용자로부터 입력받도록 설정되어 있기 때문에, 서버 측에서는 누락되었다고 판단한 것.

`fields = '__all__'`이 `article`까지 포함해 버렸고, ModelSerializer는 그걸 **필수 입력 필드**로 취급한다. 하지만 우리는 `article`을 URL에서 받기로 했으므로 사용자가 보낼 이유가 없다.

해결 방향은 **유효성 검사 목록에서 제외**하는 것, 즉 `article` 필드를 읽기 전용 필드로 설정하는 것이다.

### 읽기 전용 필드 `read_only_fields` (p.38)

**데이터를 전송받은 시점에 "유효성 검사에서 제외시키고, 데이터 조회 시에는 출력"하는 필드.**

```python
# articles/serializers.py

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('article',)
```

> **읽기 전용은 "숨김"이 아니다** — 입력에서만 빠지고 **출력에는 그대로 나온다.** 아래 응답에 `article: 5`가 찍히는 게 그 증거다. "검사 대상에서만 제외"라고 외우는 게 정확하다.

### 재요청 결과 (p.39)

`201 Created`와 함께 이런 응답이 온다.

```json
{
    "id": 3,
    "content": "댓글 1",
    "created_at": "2024-06-17T08:12:07.359953Z",
    "updated_at": "2024-06-17T08:12:07.360007Z",
    "article": 5
}
```

---

## GET · DELETE · PUT — 나머지 CRUD

### GET - List (p.41-43)

```python
# articles/urls.py

urlpatterns = [
    ...,
    path('comments/', views.comment_list),
]
```

```python
# articles/views.py

from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleSerializer, CommentSerializer


@api_view(['GET'])
def comment_list(request):
    comments = Comment.objects.all()
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)
```

목록이므로 **`many=True`** 가 붙는다.

### GET - Detail (p.44-45)

```python
# articles/urls.py

urlpatterns = [
    ...,
    path('comments/<int:comment_pk>/', views.comment_detail),
]
```

```python
# articles/views.py

@api_view(['GET'])
def comment_detail(request, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    serializer = CommentSerializer(comment)
    return Response(serializer.data)
```

### DELETE와 PUT (p.47-49)

같은 URL에 메서드만 늘려 붙인다. **하나의 view 함수가 세 메서드를 분기 처리**한다.

```python
# articles/views.py

@api_view(['GET', 'DELETE', 'PUT'])
def comment_detail(request, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)

    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
```

| 메서드 | 응답 상태 코드 | 본문 |
|---|---|---|
| `GET` | `200 OK` | 댓글 데이터 |
| `DELETE` | `204 No Content` | 없음 |
| `PUT` | `200 OK` | 수정된 댓글 데이터 |

> **생성과 수정의 Serializer 호출이 다르다** — 생성은 `CommentSerializer(data=request.data)`, 수정은 `CommentSerializer(comment, data=request.data)`처럼 **첫 번째 인자로 기존 인스턴스**를 넘긴다. 이 인자가 있으면 update, 없으면 create로 동작한다. 빠뜨리면 수정이 아니라 새 객체를 만들려 든다.

---

## 응답 데이터 재구성 — 중첩 Serializer

### 문제 상황 (p.51)

댓글을 조회하면 `article` 값이 **숫자 pk 하나**로만 나온다.

```json
{
    "id": 1,
    "content": "댓글 수정",
    "article": 5
}
```

클라이언트 입장에서는 게시글 제목이 필요한데, pk만 받아서는 게시글을 또 조회해야 한다. **응답에 제목까지 얹고 싶다.**

### Serializer 안에 Serializer 선언하기 (p.52)

> 필요한 데이터를 만들기 위한 Serializer를 내부에서 추가 선언이 가능하다.

```python
# articles/serializers.py

class CommentSerializer(serializers.ModelSerializer):

    class ArticleTitleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ('title',)

    article = ArticleTitleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        # read_only_fields = ('article',)
```

결과는 이렇게 바뀐다 (p.53).

```json
{
    "id": 1,
    "article": {
        "title": "제목 수정!"
    },
    "content": "댓글 수정",
    "created_at": "2024-06-17T08:07:33.944840Z",
    "updated_at": "2024-06-17T08:28:43.624966Z"
}
```

### 읽기 전용 필드 지정 주의사항 (p.55)

여기가 이 단원에서 가장 헷갈리는 지점이다.

> 특정 필드를 override 혹은 추가한 경우 `read_only_fields`는 동작하지 않음.
> 이런 경우 새로운 필드에 `read_only` 키워드 인자로 작성해야 함.

위 코드에서 `read_only_fields = ('article',)`이 주석 처리된 이유가 이것이다. `article` 필드를 `ArticleTitleSerializer`로 **덮어썼기 때문에** `Meta.read_only_fields`는 그 필드에 영향을 주지 못한다. 대신 `ArticleTitleSerializer(read_only=True)`처럼 **필드 선언 자리에서 직접** 지정해야 한다.

### `read_only_fields` 속성과 `read_only` 인자 (p.56)

| 구분 | 쓰는 상황 |
|---|---|
| `read_only_fields` (Meta 속성) | 기존 외래 키 필드 값을 **그대로** 응답 데이터에 제공하기 위해 지정하는 경우 |
| `read_only` (필드 인자) | 기존 외래 키 필드 값의 결과를 **다른 값으로 덮어쓰는** 경우 / 새로운 응답 데이터 값을 제공하는 경우 |

> **한 문장 판별법** — 필드를 **건드리지 않았으면** `Meta.read_only_fields`, 필드를 **다시 선언했으면** 그 선언에 `read_only=True`. 필드를 재정의해 놓고 `Meta`에만 적어두면 조용히 무시된다.

---

## 역참조 데이터 구성 — 댓글 목록 붙이기

### 목표 (p.59)

**Article → Comment 간 역참조 관계를 활용한 JSON 데이터 재구성.** 두 가지를 만든다.

1. 단일 게시글 조회 시 해당 게시글에 작성된 **댓글 목록**도 함께 붙여서 응답
2. 단일 게시글 조회 시 해당 게시글에 작성된 **댓글 개수**도 함께 붙여서 응답

앞의 중첩 Serializer는 N→1 방향(댓글에 게시글 붙이기)이었고, 이번엔 **1→N 방향**이다.

### Nested relationships (p.61)

> 모델 관계상으로 참조하는 대상은 참조되는 대상의 **표현에 포함되거나 중첩될 수 있다.** 이러한 중첩된 관계는 serializer를 필드로 사용하여 표현 가능하다.

```python
# articles/serializers.py

class ArticleSerializer(serializers.ModelSerializer):

    class CommentDetailSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ('id', 'content',)

    comment_set = CommentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = '__all__'
```

핵심은 필드 이름이 **`comment_set`** 이라는 점이다. 1편에서 본 **related manager 이름을 그대로 필드명으로 쓴다.** 그래야 DRF가 `article.comment_set`을 찾아 직렬화한다.

목록이므로 **`many=True`**, 입력받을 값이 아니므로 **`read_only=True`** 가 함께 붙는다.

응답은 게시글 데이터 안에 `comment_set` 배열이 중첩된 형태가 된다 (p.62).

---

## 댓글 개수 붙이기 — annotate

### View 로직 개선 (p.64-65)

댓글 **개수**는 모델에 없는 값이라 계산이 필요하다. 계산 위치를 view의 쿼리 단계로 잡는다.

> `annotate`는 Django ORM 함수로, SQL의 집계 함수를 활용하여 **쿼리 단계에서 데이터 가공을 수행**한다.

```python
# articles/views.py

from django.db.models import Count


@api_view(['GET', 'DELETE', 'PUT'])
def article_detail(request, article_pk):
    article = Article.objects.annotate(num_of_comments=Count('comment')).get(pk=article_pk)
```

이렇게 하면 조회된 `article` 객체에 **`num_of_comments`라는 "주석(annotate) 필드"** 가 포함된다. 모델에 정의된 적 없는 필드지만, 이 쿼리로 가져온 객체에는 실제로 붙어 있다.

`Count('comment')`의 `'comment'`는 **역참조 이름**이다(`comment_set`의 기준이 되는 모델명). 여기에 `_set`을 붙이지 않는다는 점을 주의한다.

> **왜 파이썬에서 세지 않고 `annotate`인가** — `len(article.comment_set.all())`로도 개수는 나오지만, 그러려면 댓글 레코드를 전부 DB에서 끌어와야 한다. `annotate`는 SQL의 `COUNT`로 **DB가 세서 숫자 하나만** 돌려준다. 목록 API처럼 게시글이 여러 개일 때 성능 차이가 커진다.

---

## SerializerMethodField

### 무엇인가 (p.66-67, 70)

`annotate`로 값은 만들었지만, 그 값을 **응답 JSON에 실어 보내는 일**은 Serializer의 몫이다. 그 통로가 `SerializerMethodField`다.

- **DRF에서 제공하는 읽기 전용 필드**
- **Serializer에서 추가적인 데이터 가공을 하고 싶을 때 사용**
- 예: 특정 필드 값을 조합해 새로운 문자열 필드를 만들거나, 부가적인 계산(비율, 합계, 평균)을 하는 경우

```python
# articles/serializers.py

class ArticleSerializer(serializers.ModelSerializer):

    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        ...

    def get_num_of_comments(self, obj):
        # 여기서 obj = Serializer가 처리하는 Article 인스턴스
        # view에서 annotate 한 필드를 그대로 사용 가능
        return obj.num_of_comments
```

이제 `serializer.data`를 반환하면 `get_num_of_comments` 메서드가 실행되어 `num_of_comments` 값이 자동으로 포함된다. **view에서 `data`를 딕셔너리로 변환하거나 수정할 필요 없이** `serializer.data`를 바로 반환해도 JSON 응답에 값이 반영된다.

### 동작 원리 (p.71-73)

> `SerializerMethodField`를 Serializer 클래스 내에서 필드로 선언하면, DRF는 **`get_<필드명>`이라는 이름을 가진 메서드를 자동으로 찾는다.**

```python
class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email',)

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
```

- `full_name = serializers.SerializerMethodField()`라고 선언하면 → DRF는 `get_full_name(self, obj)` 메서드를 찾아 그 반환값을 직렬화 결과에 넣는다
- **`obj`는 현재 직렬화 중인 모델 인스턴스**이며, 이 메서드에서 `obj`의 속성이나 `annotate`된 필드를 활용해 새 값을 만들 수 있다

### 주의사항 (p.74)

- **읽기 전용**으로, 생성(POST)·수정(PUT) 요청 시에는 사용되지 않는다
- `get_` 메서드는 반드시 **`(self, obj)` 형태**로 정의해야 하며, `obj`는 현재 직렬화 중인 모델 인스턴스를 의미한다

> **이름이 안 맞으면 조용히 실패한다** — 필드명이 `num_of_comments`인데 메서드를 `get_comments_count`로 쓰면 DRF는 메서드를 찾지 못한다. `get_` + 필드명이 **정확히** 일치해야 한다.

### 사용 목적 (p.75)

| 항목 | 내용 |
|---|---|
| 유연성 | 다양한 계산 로직을 손쉽게 추가 가능 |
| 가독성 | 데이터 변환 과정을 Serializer 내부 메서드로 명확히 분리 |
| 유지보수성 | view나 model에 비해 Serializer 측 로직 변경이 용이 |
| 일관성 | view에서 별도로 로직 수정 없이도 직렬화 결과를 제어 |

> **역할 분담으로 외우기** — `annotate`는 **view/queryset 계층**에서 값을 만들고, `SerializerMethodField`는 **serializer 계층**에서 그 값을 응답에 실어 보낸다. 이 분담의 근거는 4편의 마지막 항목에서 다시 정리된다.

---

## 정리 체크리스트

- [ ] 댓글 생성 URL만 `articles/<pk>/comments/` 형태인 이유를 말할 수 있다
- [ ] `article` 필드 때문에 400이 나는 원인과 해결책을 설명할 수 있다
- [ ] 읽기 전용 필드가 입력·출력 중 어느 쪽에서 빠지는지 안다
- [ ] `read_only_fields`와 `read_only`를 언제 쓰는지 구분할 수 있다
- [ ] 중첩 Serializer 필드명을 `comment_set`으로 쓰는 이유를 안다
- [ ] `annotate`와 `SerializerMethodField`의 담당 계층을 구분할 수 있다
- [ ] `get_<필드명>` 규칙과 `obj`의 정체를 설명할 수 있다

## 복습 문제

1. `fields = '__all__'`인 `CommentSerializer`로 댓글을 생성하면 왜 400이 나는가?
   <details><summary>답</summary>`'__all__'`이 외래 키 `article`까지 포함시키고, ModelSerializer는 이를 필수 입력 필드로 취급한다. 사용자는 `content`만 보내므로 서버는 `article`이 누락됐다고 판단한다. `read_only_fields = ('article',)`로 유효성 검사에서 제외하면 해결된다.</details>

2. `serializer.save(article=article)`에서 `article`을 여기서 넘기는 이유는?
   <details><summary>답</summary>`article`은 요청 본문이 아니라 URL에서 온 값이라 유효성 검사 대상이 아니다. 검사를 통과한 뒤 저장 시점에 추가 데이터로 직접 넘긴다. `save()`는 저장 과정에서 추가 데이터를 받을 수 있다.</details>

3. 필드를 다시 선언했는데 `Meta.read_only_fields`에만 적어두면 어떻게 되는가?
   <details><summary>답</summary>동작하지 않는다. 특정 필드를 override하거나 추가한 경우 `read_only_fields`는 그 필드에 적용되지 않으므로, 필드 선언 자리에 `read_only=True` 인자를 직접 써야 한다.</details>

4. 중첩 Serializer 필드 이름을 `comments`가 아니라 `comment_set`으로 쓴 이유는?
   <details><summary>답</summary>DRF가 `article.comment_set`이라는 related manager를 찾아 직렬화하기 때문이다. N:1의 기본 역참조 이름이 `모델명_set`이므로 필드명도 여기에 맞춘다. (`related_name`을 지정했다면 그 이름을 쓴다.)</details>

5. `Count('comment')`인가 `Count('comment_set')`인가?
   <details><summary>답</summary>`Count('comment')`다. ORM의 조회 경로에서는 `_set` 없이 소문자 모델명을 쓴다. `_set`이 붙는 것은 파이썬 인스턴스에서 related manager에 접근할 때다.</details>

6. `annotate`로 만든 값이 응답 JSON에 저절로 들어가는가?
   <details><summary>답</summary>아니다. `annotate`는 조회된 객체에 속성을 붙일 뿐이고, 모델에 없는 필드라 Serializer가 알지 못한다. `SerializerMethodField`로 선언하고 `get_<필드명>`에서 `obj.num_of_comments`를 반환해야 응답에 실린다.</details>
