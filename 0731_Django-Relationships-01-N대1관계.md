# N:1 관계 — Many to one relationships

> 시리즈: **01 N:1 관계** · [02 DRF with N:1](Django-Relationships-02-DRF-N대1.md) · [03 M:N 관계](Django-Relationships-03-N대M관계.md) · [04 실습과 shortcuts](Django-Relationships-04-실습과-shortcuts.md)

> 출처: `16기_데이터트랙_0731_Django_Relationships.pdf` (총 119페이지) · 정리일: 2026-07-31
> 페이지 표기는 PDF 기준. 이 자료는 슬라이드 인쇄 번호와 PDF 번호가 일치한다.

## 한눈에 보기

- 두 테이블이 N:1로 엮인다는 게 데이터 구조상 정확히 무슨 뜻인가
- 외래 키를 **어느 쪽 테이블에** 두어야 하는가, 그리고 왜 그쪽인가
- `ForeignKey(to, on_delete)`의 두 필수 인자가 각각 무엇을 결정하는가
- 참조(N→1)는 되는데 역참조(1→N)는 왜 별도 기능이 필요한가
- `article.comment_set.all()`이라는 이름은 어디서 유래했는가

## 목차

1. [N:1 관계란 무엇인가](#n1-관계란-무엇인가) (p.6-10)
2. [댓글 모델 정의 — ForeignKey](#댓글-모델-정의--foreignkey) (p.11-17)
3. [역참조와 related manager](#역참조와-related-manager) (p.19-26)

---

## N:1 관계란 무엇인가

### 정의 (p.6)

**한 테이블의 0개 이상의 레코드가 다른 테이블의 레코드 한 개와 관련된 관계.** `N:1` 또는 `1:N`으로 쓴다.

여기서 놓치기 쉬운 단어가 **"0개 이상"** 이다. N쪽이 반드시 1개 이상 있어야 하는 게 아니라, 하나도 없어도 관계는 성립한다. 댓글이 하나도 없는 게시글이 존재할 수 있다는 뜻이다.

### Comment(N) - Article(1) (p.7-8)

이 자료가 끝까지 끌고 가는 예시는 **댓글과 게시글**이다.

> 0개 이상의 댓글은 1개의 게시글에 작성될 수 있다.

이 한 문장을 방향으로 풀면 이렇게 된다.

- 댓글 하나 → 게시글 하나 (반드시 하나)
- 게시글 하나 → 댓글 0개 이상

**N쪽이 Comment, 1쪽이 Article**이다.

### 테이블 관계 (p.9-10)

관계를 맺기 전 두 테이블은 각자 독립적이다.

| Comment | Article |
|---|---|
| id | id |
| content | title |
| created_at | content |
| updated_at | created_at |
| | updated_at |

여기에 관계를 추가하면, **Comment 테이블 쪽에 `Article`에 대한 외래 키 컬럼이 하나 붙는다.**

```text
Comment                        Article
├─ id                          ├─ id
├─ content                     ├─ title
├─ created_at                  ├─ content
├─ updated_at                  ├─ created_at
└─ Article에 대한 외래 키  ───▶ └─ updated_at
```

> **왜 N쪽에 외래 키를 두는가** — 반대로 Article 쪽에 댓글 정보를 담으려면 댓글 개수만큼 컬럼이 필요해진다. 댓글이 몇 개 달릴지 미리 알 수 없으므로 불가능하다. 반면 댓글 입장에서 소속 게시글은 **항상 정확히 하나**이므로 컬럼 하나로 표현된다. **"항상 1개인 쪽을 가리키는 컬럼"** 이라 외래 키는 언제나 N쪽에 놓인다.

---

## 댓글 모델 정의 — ForeignKey

### `ForeignKey()` (p.12-13)

**N:1 관계를 설정하는 모델 필드**다.

```python
# articles/models.py

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

작성 시 두 가지 규칙이 강조된다.

- **`ForeignKey` 클래스의 인스턴스 이름은 참조하는 모델 클래스 이름의 단수형으로 작성하는 것을 권장** — `Article`을 참조하므로 필드명은 `article`
- **외래 키는 `ForeignKey` 클래스를 작성하는 위치와 관계없이 테이블 필드 마지막에 생성됨** — 위 코드처럼 맨 위에 써도 실제 테이블에서는 마지막 컬럼이 된다

### `ForeignKey(to, on_delete)` (p.14-15)

두 인자는 필수다.

| 인자 | 의미 |
|---|---|
| `to` | 참조하는 모델 class 이름 |
| `on_delete` | 외래 키가 참조하는 객체(1)가 사라졌을 때, 외래 키를 가진 객체(N)를 어떻게 처리할지를 정의하는 설정 |

`on_delete`의 목적은 한 단어로 **데이터 무결성**이다. 게시글이 지워졌는데 그 게시글을 가리키는 댓글이 그대로 남아 있으면, 존재하지 않는 대상을 가리키는 유령 레코드가 된다. 그런 상태를 막기 위해 "이럴 땐 이렇게 처리하라"를 미리 못 박아 두는 것이다.

### `on_delete`의 `CASCADE` (p.16)

**부모 객체(참조된 객체)가 삭제됐을 때 이를 참조하는 객체도 삭제.**

게시글을 지우면 그 게시글에 달린 댓글도 함께 지워진다. 실습에서는 이 값을 쓴다.

> 기타 설정 값은 공식 문서 참고 — <https://docs.djangoproject.com/en/5.2/ref/models/fields/#arguments>

### Migration 이후 테이블 확인 (p.17)

`makemigrations` / `migrate` 이후 `articles_comment` 테이블을 열어보면 이렇게 되어 있다.

```text
articles_comment
└─ Columns
   ├─ id          INTEGER      (PK)
   ├─ content     varchar(200)
   ├─ created_at  datetime
   ├─ updated_at  datetime
   └─ article_id  bigint       (FK)
```

모델에는 `article`이라고 썼는데 **실제 컬럼은 `article_id`** 로 만들어진다. 참조하는 클래스 이름의 소문자(단수형)로 필드명을 쓰라고 권장했던 이유가 여기 있다. 그렇게 써야 컬럼 이름이 `article_id`처럼 자연스럽게 읽힌다.

> **주의 — 슬라이드의 이름 규칙 표기** 
> 슬라이드에는 이름 규칙이 `'참조 대상 클래스 이름' + '_' + '클래스 이름'`으로 적혀 있다. 다만 실제로 생성된 컬럼은 `article_id`이므로, 뒷부분은 `'id'`로 읽는 편이 자료의 화면과 맞는다. 즉 **`<필드명>_id`** 가 실제 동작이다. 시험에 나온다면 결과값인 `article_id`를 기준으로 답하는 것이 안전하다.

---

## 역참조와 related manager

### 참조와 역참조는 대칭이 아니다 (p.21-22)

- **참조** — N에서 1을 조회. `comment.article`
- **역참조** — **N:1 관계에서 1에서 N을 참조하거나 조회하는 것.** `1 → N`

문제는 이 둘이 대칭이 아니라는 점이다.

> N은 외래 키를 가지고 있어 물리적으로 참조가 가능하지만, 1은 N에 대한 참조 방법이 존재하지 않아 별도의 역참조 기능이 필요하다.

Comment 테이블에는 `article_id` 컬럼이 실제로 존재하므로 `comment.article`은 컬럼 값을 따라가면 된다. 반대로 Article 테이블에는 댓글을 가리키는 컬럼이 **아예 없다.** 그래서 Django가 별도의 도구를 만들어 준다.

### related manager (p.23-25)

```python
article.comment_set.all()
```

세 부분으로 뜯어 읽는다.

| 구간 | 정체 |
|---|---|
| `article` | 모델 인스턴스 |
| `comment_set` | **related manager** (역참조 이름) |
| `all()` | QuerySet API |

의미는 **특정 게시글에 작성된 댓글 전체를 조회하는 명령**이다.

**related manager**는 N:1 혹은 M:N 관계에서 역참조 시에 사용하는 매니저다. 핵심은 이 문장이다.

> `objects` 매니저를 통해 QuerySet API를 사용했던 것처럼, related manager를 통해 QuerySet API를 사용할 수 있게 된다.

즉 `Comment.objects.filter(...)`에서 쓰던 API를 `article.comment_set.filter(...)`에서 그대로 쓸 수 있다. 새로운 문법을 배우는 게 아니라 **진입점만 바뀌는 것**이다.

### 이름 규칙 (p.26)

**N:1 관계에서 생성되는 related manager의 이름은 참조하는 `"모델명_set"` 이름 규칙으로 만들어진다.**

| 방향 | 코드 | 결과 |
|---|---|---|
| 특정 댓글의 게시글 참조 (Comment → Article) | `comment.article` | Article 인스턴스 1개 |
| 특정 게시글의 댓글 목록 참조 (Article → Comment) | `article.comment_set.all()` | Comment QuerySet |

> **두 방향의 반환 타입이 다르다** — 참조는 인스턴스 하나가 나오고, 역참조는 QuerySet이 나온다. `comment.article.title`은 되지만 `article.comment_set.content`는 안 된다. 역참조 결과는 목록이므로 `.all()`, `.filter()`, `.count()` 같은 QuerySet API를 거쳐야 한다.

> **`_set`이라는 이름은 바꿀 수 있다** — `related_name` 인자를 쓰면 된다. 3편에서 이 이름이 **충돌해서 migration이 실패하는 상황**을 다루는데, 그때 반드시 필요해진다.

---

## 정리 체크리스트

- [ ] N:1에서 "0개 이상"이 무엇을 허용하는 표현인지 설명할 수 있다
- [ ] 외래 키가 N쪽 테이블에 놓이는 이유를 컬럼 개수로 설명할 수 있다
- [ ] `ForeignKey`의 두 필수 인자와 각각의 역할을 말할 수 있다
- [ ] `on_delete=CASCADE`의 동작을 게시글–댓글로 설명할 수 있다
- [ ] 모델 필드명 `article`이 DB 컬럼 `article_id`가 되는 규칙을 안다
- [ ] 1→N 조회에 별도 기능이 필요한 이유를 테이블 구조로 설명할 수 있다
- [ ] `article.comment_set.all()`의 세 구간을 각각 이름 붙여 말할 수 있다

## 복습 문제

1. 외래 키는 왜 Article이 아니라 Comment 테이블에 생기는가?
   <details><summary>답</summary>Article 쪽에 두려면 달릴 댓글 개수만큼 컬럼이 필요한데 그 수를 미리 알 수 없다. 반대로 댓글 입장에서 소속 게시글은 항상 정확히 하나이므로 컬럼 하나로 표현된다. 그래서 외래 키는 항상 N쪽에 놓인다.</details>

2. `on_delete`가 정의하는 것은 정확히 어떤 상황에 대한 처리인가?
   <details><summary>답</summary>외래 키가 참조하는 객체(1쪽)가 삭제됐을 때, 그 외래 키를 가진 객체(N쪽)를 어떻게 처리할지를 정의한다. 목적은 데이터 무결성 유지다.</details>

3. 모델에 `article = models.ForeignKey(...)`라고 썼는데 DB 컬럼 이름이 `article`이 아닌 이유는?
   <details><summary>답</summary>Django가 외래 키 컬럼을 만들 때 필드명 뒤에 `_id`를 붙이기 때문이다. 그래서 `article_id`가 된다. 또한 이 컬럼은 작성 위치와 무관하게 테이블 필드 마지막에 생성된다.</details>

4. `comment.article`과 `article.comment_set.all()`의 반환 타입은 각각 무엇인가?
   <details><summary>답</summary>앞은 Article 모델 인스턴스 하나, 뒤는 Comment QuerySet이다. N→1은 대상이 항상 하나라 인스턴스가 나오고, 1→N은 여러 개일 수 있어 QuerySet이 나온다.</details>

5. related manager가 있어서 좋은 점을 한 문장으로 말하면?
   <details><summary>답</summary>`objects` 매니저로 쓰던 QuerySet API를 역참조에서도 똑같이 쓸 수 있다. 새 문법을 배우는 게 아니라 진입점만 바뀐다.</details>
