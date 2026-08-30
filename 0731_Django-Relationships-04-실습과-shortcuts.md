# 기능 구현과 Django shortcuts

> 시리즈: [01 N:1 관계](0731_Django-Relationships-01-N대1관계.md) · [02 DRF with N:1](0731_Django-Relationships-02-DRF-N대1.md) · [03 M:N 관계](0731_Django-Relationships-03-N대M관계.md) · **04 실습과 shortcuts**

> 출처: `16기_데이터트랙_0731_Django_Relationships.pdf` (총 119페이지) · 정리일: 2026-07-31
> 페이지 표기는 PDF 기준

## 한눈에 보기

- M:N 관계를 실제 API로 만들면 어떤 모양인가 (보조 강사 등록/해제 토글)
- `Model.objects.get()`이 왜 500 에러를 내는가
- `get_object_or_404` / `get_list_or_404`는 무엇을 바꿔주는가
- 500이 아니라 404를 돌려줘야 하는 이유
- view와 serializer의 역할을 어떻게 나눠야 하는가

## 목차

1. [보조 강사 기능 구현](#보조-강사-기능-구현) (p.104-107)
2. [올바르게 404 응답하기](#올바르게-404-응답하기) (p.109-116)
3. [View와 Serializer의 역할](#view와-serializer의-역할) (p.118)

---

## 보조 강사 기능 구현

### URL 작성 (p.104)

```python
# config/urls.py

urlpatterns = [
    path("courses/", include("courses.urls")),
]
```

```python
# courses/urls.py

urlpatterns = [
    path("", views.courses),
]
```

### view 함수 작성 (p.105)

```python
# courses/views.py

@api_view(["POST"])
def assistant(request, course_pk, teacher_pk):
    course = get_object_or_404(Course, pk=course_pk)
    teacher = get_object_or_404(Teacher, pk=teacher_pk)

    if teacher in course.assistant_teachers.all():
        course.assistant_teachers.remove(teacher)
    else:
        course.assistant_teachers.add(teacher)

    return Response(CourseSerializer(course).data, status=status.HTTP_200_OK)
```

읽는 순서는 이렇다.

1. URL에서 받은 pk 두 개로 `Course`와 `Teacher`를 각각 조회한다
2. **이미 보조 강사로 등록돼 있으면 `remove()`, 아니면 `add()`** — 같은 요청이 등록과 해제를 번갈아 수행하는 **토글** 구조다
3. 변경된 `course`를 직렬화해 `200 OK`로 반환한다

> **토글 판정에 `.all()`이 붙는 이유** — `course.assistant_teachers`는 related manager(매니저 객체)일 뿐이라 `in` 연산의 대상이 아니다. `.all()`로 QuerySet을 얻어야 포함 여부를 물을 수 있다.

> **`add()`의 중복 무시 성질과 짝이 맞는다** — 3편에서 본 대로 `add()`는 이미 있는 관계를 복제하지 않는다. 덕분에 이 코드는 중복 등록을 따로 방어할 필요가 없고, 분기의 목적이 "중복 방지"가 아니라 **"해제 기능 제공"** 이라는 점이 분명해진다.

### 응답 확인 (p.106-107)

같은 URL로 두 번 POST하면 결과가 이렇게 갈린다.

```json
// 1회차 — 등록됨
{
    "id": 1,
    "name": "Django",
    "main_teacher": { "id": 4, "name": "홍길동" },
    "assistant_teachers": [
        { "id": 1, "name": "안정복" }
    ]
}
```

```json
// 2회차 — 해제됨
{
    "id": 1,
    "name": "Django",
    "main_teacher": { "id": 4, "name": "홍길동" },
    "assistant_teachers": []
}
```

`main_teacher`(N:1)와 `assistant_teachers`(M:N)가 **한 응답에 함께** 나오는 것이 3편에서 만든 두 관계의 결과다. 앞은 객체 하나, 뒤는 배열이라는 점도 관계 종류를 그대로 반영한다.

---

## 올바르게 404 응답하기

### Django shortcuts functions (p.110)

`django.shortcuts`가 제공하는 함수들이다.

- `redirect()`
- `get_object_or_404()`
- `get_list_or_404()`

### `get_object_or_404()` (p.111)

> 모델 manager `objects`의 `get()`을 호출하지만, 해당 객체가 없을 땐 기존 `DoesNotExist` 예외 대신 **`Http404`를 raise** 함.

### 적용 (p.112)

```python
# articles/views.py

from django.shortcuts import get_object_or_404

# 변경 전
article = Article.objects.get(pk=article_pk)
comment = Comment.objects.get(pk=comment_pk)

# 변경 후
article = get_object_or_404(Article, pk=article_pk)
comment = get_object_or_404(Comment, pk=comment_pk)

# annotate가 걸린 queryset도 그대로 넘길 수 있다
article = get_object_or_404(
    Article.objects.annotate(num_of_comments=Count('comment')),
    pk=article_pk,
)
```

> **첫 번째 인자는 모델일 수도, queryset일 수도 있다** — 2편에서 만든 `annotate` 쿼리처럼 이미 가공된 queryset을 그대로 넘길 수 있다. 그래서 `get_object_or_404`를 도입한다고 해서 기존 최적화를 포기할 필요가 없다.

### `get_list_or_404()` (p.113)

> 모델 manager `objects`에서 `filter()`의 결과를 반환하고, 해당 객체 목록이 없을 땐 **`Http404`를 raise** 함.

### 적용 (p.114)

```python
# articles/views.py

from django.shortcuts import get_list_or_404

# 변경 전
articles = Article.objects.all()
comments = Comment.objects.all()

# 변경 후
articles = get_list_or_404(Article)
comments = get_list_or_404(Comment)
```

> **빈 목록의 의미가 달라진다** — `objects.all()`은 결과가 없으면 빈 리스트를 `200 OK`로 돌려주지만, `get_list_or_404`는 **404를 낸다.** "데이터가 하나도 없는 상태"를 정상으로 볼지 오류로 볼지는 API 설계 판단이므로, 목록 API에 무조건 적용하기 전에 한 번 생각해 볼 지점이다.

### 적용 전후 비교 (p.115)

존재하지 않는 게시글을 조회했을 때 (`GET /api/v1/articles/100/`)

| | 상태 코드 | 응답 본문 |
|---|---|---|
| 적용 전 | `500 Internal Server Error` | Django 디버그 HTML 페이지 |
| 적용 후 | `404 Not Found` | `{ "detail": "Not found." }` |

### 왜 사용해야 할까 (p.116)

> 클라이언트에게 "서버에 오류가 발생하여 요청을 수행할 수 없다(500)"라는 **원인이 정확하지 않은 에러를 제공하기보다는**, 적절한 예외 처리를 통해 클라이언트에게 **보다 정확한 에러 현황을 전달**하는 것도 매우 중요한 개발 요소 중 하나이기 때문.

| 상태 코드 | 클라이언트가 받는 메시지 | 다음 행동 |
|---|---|---|
| `500` | 서버가 고장났다 | 할 수 있는 게 없다. 재시도밖에 |
| `404` | 그런 데이터가 없다 | 잘못된 링크임을 안내하거나 목록으로 돌려보낸다 |

> **응답 본문 형식도 함께 바뀐다** — 적용 전에는 Django의 디버그 HTML이 통째로 날아간다. JSON을 기대하는 API 클라이언트는 파싱조차 못 한다. 적용 후에는 `{"detail": "Not found."}`라는 **JSON**이 오므로 클라이언트가 정상적으로 처리할 수 있다. 상태 코드뿐 아니라 **콘텐츠 타입이 정상화된다**는 점도 실질적인 이득이다.

---

## View와 Serializer의 역할

이 자료의 마지막 개념 정리다 (p.118).

> Django에서는 비즈니스 로직(데이터 가공, `annotate`, 필터링)을 **view나 queryset 로직에서 처리**하고, serializer는 **그 결과물을 직렬화하는 역할에 집중**하는 것이 일반적인 권장사항.

복잡한 query 로직은 View 함수에서 진행한다.

- 여러 모델을 조인하거나 복잡한 집계가 필요한 경우 View 함수에서 처리
- 필요한 경우 View 함수에서 **`select_related()`나 `prefetch_related()`** 를 사용하여 query를 최적화

| 계층 | 담당 |
|---|---|
| View / QuerySet | 데이터 가공, `annotate`, 필터링, 조인, 집계, 쿼리 최적화 |
| Serializer | 그 결과물의 직렬화 |

> **2편의 구조가 이 원칙의 사례였다** — 댓글 개수를 view에서 `annotate`로 만들고, serializer는 `SerializerMethodField`로 그 값을 꺼내 쓰기만 했다. 계산을 serializer 안에서 직접 했다면 게시글마다 추가 쿼리가 발생했을 것이다. 원칙과 성능이 같은 방향을 가리키는 셈이다.

> **`select_related`와 `prefetch_related`의 갈림** — 이름만 언급되고 상세 설명은 이 자료 범위 밖이지만, 방향으로 기억해 두면 좋다. N:1처럼 **단일 객체를 따라가는** 관계는 `select_related`(SQL JOIN), M:N이나 1:N처럼 **여러 개를 따라가는** 관계는 `prefetch_related`(별도 쿼리 후 파이썬에서 결합)를 쓴다.

---

## 정리 체크리스트

- [ ] 보조 강사 토글 view의 분기가 무엇을 위한 것인지 설명할 수 있다
- [ ] `course.assistant_teachers`에 `.all()`을 붙이는 이유를 안다
- [ ] `get_object_or_404`가 바꾸는 것이 무엇인지 한 문장으로 말할 수 있다
- [ ] `get_object_or_404`에 queryset을 넘길 수 있다는 것을 안다
- [ ] `get_list_or_404` 적용 시 빈 목록의 취급이 어떻게 달라지는지 안다
- [ ] 500 대신 404를 주는 것이 왜 나은지 클라이언트 관점에서 설명할 수 있다
- [ ] view와 serializer의 역할 분담 원칙을 말할 수 있다

## 복습 문제

1. 보조 강사 토글 view에서 `if teacher in course.assistant_teachers.all():` 분기의 목적은?
   <details><summary>답</summary>중복 방지가 아니라 해제 기능 제공이다. `add()`는 이미 존재하는 관계를 복제하지 않으므로 중복은 자동으로 막힌다. 이 분기는 이미 등록된 강사면 `remove()`로 빼주기 위한 것이다.</details>

2. `Article.objects.get(pk=999)`로 없는 객체를 조회하면 어떤 일이 벌어지는가?
   <details><summary>답</summary>`DoesNotExist` 예외가 발생하고, 처리되지 않으면 500 Internal Server Error가 응답된다. 본문은 Django 디버그 HTML이라 JSON을 기대하는 클라이언트는 파싱도 못 한다.</details>

3. `get_object_or_404`와 `get_list_or_404`는 각각 어떤 메서드를 대체하는가?
   <details><summary>답</summary>앞은 `objects.get()`, 뒤는 `objects.filter()`의 결과를 반환한다. 둘 다 대상이 없을 때 `Http404`를 raise한다는 점이 공통이다.</details>

4. 500 대신 404를 응답하면 클라이언트에게 무엇이 좋아지는가?
   <details><summary>답</summary>원인이 불분명한 서버 오류 대신 "그런 데이터가 없다"는 정확한 정보를 받는다. 그래서 잘못된 링크 안내나 목록 복귀 같은 적절한 처리를 할 수 있다. 응답 본문도 HTML이 아닌 JSON으로 돌아온다.</details>

5. 데이터 가공 로직은 view와 serializer 중 어디에 두는 것이 권장되는가?
   <details><summary>답</summary>view 또는 queryset 로직이다. `annotate`, 필터링, 조인, 집계는 view에서 처리하고 serializer는 그 결과의 직렬화에 집중한다. 복잡한 쿼리는 `select_related()`나 `prefetch_related()`로 최적화한다.</details>
