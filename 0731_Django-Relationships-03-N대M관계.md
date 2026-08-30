# M:N 관계 — Many to many relationships

> 시리즈: [01 N:1 관계](0731_Django-Relationships-01-N대1관계.md) · [02 DRF with N:1](0731_Django-Relationships-02-DRF-N대1.md) · **03 M:N 관계** · [04 실습과 shortcuts](0731_Django-Relationships-04-실습과-shortcuts.md)

> 출처: `16기_데이터트랙_0731_Django_Relationships.pdf` (총 119페이지) · 정리일: 2026-07-31
> 페이지 표기는 PDF 기준

## 한눈에 보기

- N:1만으로 표현할 수 없는 관계는 어떤 모양인가
- 중개 모델(중개 테이블)이 왜 필연적으로 등장하는가
- `ManyToManyField` 하나 추가했을 뿐인데 migration이 깨지는 이유
- `related_name` · `symmetrical` · `through` 세 인자는 각각 무엇을 조절하는가
- M:N 관계에 데이터를 넣고 빼는 `add()` / `remove()`

## 목차

1. [M:N 관계란 무엇인가](#mn-관계란-무엇인가) (p.78-79)
2. [실습 환경 — Teacher와 Course](#실습-환경--teacher와-course) (p.82-88)
3. [ManyToManyField와 역참조 매니저 충돌](#manytomanyfield와-역참조-매니저-충돌) (p.89-95)
4. [ManyToManyField의 대표 인자 3가지](#manytomanyfield의-대표-인자-3가지) (p.96-100)
5. [M:N에서의 대표 메서드](#mn에서의-대표-메서드) (p.101)

---

## M:N 관계란 무엇인가

### 정의 (p.78)

**한 테이블의 0개 이상의 레코드가 다른 테이블의 0개 이상의 레코드와 관련된 경우.** `N:M` 또는 `M:N`으로 쓴다.

> 양쪽 모두에서 N:1 관계를 가짐

이 마지막 줄이 핵심이다. M:N은 새로운 종류의 관계가 아니라 **양방향 N:1이 겹친 것**이다. 그래서 중개 테이블 하나를 두고 양쪽에서 외래 키를 거는 구조로 풀린다.

### 왜 외래 키 하나로는 안 되는가

1편에서 외래 키는 "항상 1개인 쪽을 가리키는 컬럼"이라고 정리했다. M:N에서는 **양쪽 다 여러 개**라서 그 조건이 성립하지 않는다. 어느 쪽에 컬럼을 두든 값이 여러 개 필요해진다.

그래서 관계 자체를 저장하는 **제3의 테이블**이 필요하다. 이것이 중개 테이블(중개 모델)이다.

```text
Teacher            중개 모델              Course
  id     ◀──── teacher_id  course_id ────▶  id
  name                                      name
```

중개 테이블의 한 행은 "이 강사와 이 강좌가 연결되어 있다"는 사실 하나를 뜻한다. 연결이 늘면 행이 늘 뿐이므로, 개수 제한이 사라진다.

### Django의 처리 (p.79)

> Django에서는 **`ManyToManyField`가 중개 모델을 자동으로 생성**한다.

개발자가 중개 테이블을 직접 만들 필요가 없다. 필드 하나만 선언하면 Django가 알아서 테이블을 만든다. 단, **추가 데이터를 담아야 할 때는 직접 만든다** — 이 경우가 뒤에 나올 `through`다.

---

## 실습 환경 — Teacher와 Course

### 스켈레톤 프로젝트 준비 (p.82)

```bash
$ python -m venv venv
$ source venv/Scripts/activate
$ pip install -r requirements.txt
```

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

외부 패키지 및 라이브러리는 `requirements.txt`에 작성되어 있다.

### 기존 모델 구조 (p.83-84)

```python
# teachers/models.py

class Teacher(models.Model):
    name = models.CharField(max_length=100)
```

```python
# courses/models.py

class Course(models.Model):
    name = models.CharField(max_length=100)
    main_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
```

> 현재 `main_teacher` 필드를 통해 `Teacher` 클래스를 참조하는 **N:1 관계로 설정되어 있다.** (`main_teacher` 필드는 강좌의 주 강사)

**이미 N:1 관계가 하나 존재한다**는 점을 기억해야 한다. 뒤의 충돌은 전부 여기서 비롯된다.

### 추가하려는 관계 (p.85-88)

강좌와 **보조 강사** 사이에 M:N 관계를 설정하려 한다.

> Teacher(M) - Course(N)
> 0명 이상의 보조 강사는 0개 이상의 강좌와 관련
> 강좌는 0명 이상의 보조 강사를 가질 수 있고, 강사는 0개 이상의 강좌에 보조 강사로 참여할 수 있다.

정리하면 Teacher와 Course 사이에 **관계가 두 개** 생긴다.

| 관계 | 종류 | 필드 |
|---|---|---|
| 주 강사 | N:1 | `main_teacher` |
| 보조 강사 | M:N | `assistant_teachers` |

---

## ManyToManyField와 역참조 매니저 충돌

### 필드 추가 (p.89)

```python
# courses/models.py

class Course(models.Model):
    name = models.CharField(max_length=100)
    main_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    assistant_teachers = models.ManyToManyField(Teacher)
```

### Migration 진행 후 에러 발생 (p.90)

여기서 migration이 실패한다.

### 역참조 매니저 충돌 (p.91-92)

원인은 **역참조 이름이 겹치는 것**이다.

- `assistant_teachers` 필드 생성 시 자동으로 역참조 매니저 `.course_set`이 생성됨
- 그러나 이전 N:1(`Course` - `Teacher`) 관계에서 **이미 같은 이름의 매니저를 사용 중**
  - `teacher.course_set.all()` → 해당 강사가 주 강사로 참여하는 모든 강좌

결과적으로 이렇게 된다.

> **'주 강사로 참여하는 강좌(`teacher.course_set`)'** 와 **'보조 강사로 참여하는 강좌(`teacher.course_set`)'** 를 구분할 수 없게 됨.

두 관계가 같은 이름을 요구하니 Django가 거부한다.

> 해결: `teacher`와 관계된 `ForeignKey` 혹은 `ManyToManyField` **둘 중 하나에 `related_name` 작성 필요**

> **원본 슬라이드 표기 주의 (p.91, p.95)** 
> 이 두 장에는 예시 코드가 `user.article_set.all()`, `user.assistant_courses`로 적혀 있다. 앞 단원(Article/Comment)의 예시가 그대로 남은 것으로 보이며, 현재 맥락에서는 **`teacher.course_set.all()`, `teacher.assistant_courses`** 가 맞다. p.92에는 `teacher.course_set.all()`로 올바르게 적혀 있다. 또한 이 구간의 슬라이드 머리말이 "좋아요 기능 구현"으로 되어 있으나 내용은 Teacher–Course 예시다.

### related_name 작성 후 재진행 (p.93)

```python
# courses/models.py

class Course(models.Model):
    name = models.CharField(max_length=100)
    main_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    assistant_teachers = models.ManyToManyField(Teacher, related_name='assistant_courses')
```

M:N 쪽 역참조 이름을 `assistant_courses`로 바꿨으므로 `course_set`은 N:1 전용으로 남는다. 이제 migration이 통과한다.

### 생성된 중개 테이블 (p.94)

```text
courses_course_assistant_teachers
└─ Columns
   ├─ id          INTEGER   (PK)
   ├─ course_id   bigint    (FK → Course)
   └─ teacher_id  bigint    (FK → Teacher)
```

테이블 이름은 `앱이름_모델명_필드명` 규칙으로 만들어지고, 컬럼은 **양쪽 모델을 가리키는 외래 키 두 개**뿐이다. "M:N은 양방향 N:1이 겹친 것"이라는 정의가 그대로 테이블로 나타난 모습이다.

### 사용 가능한 전체 related manager (p.95)

Teacher와 Course 사이에 이제 네 방향의 접근이 가능하다.

| 코드 | 의미 | 관계 |
|---|---|---|
| `course.main_teacher` | 강좌의 주 강사 정보 | N:1 |
| `teacher.course_set` | 강사가 주 강사로 참여하는 강좌 정보 | 1:N |
| `course.assistant_teachers` | 강좌의 보조 강사 정보 | M:N |
| `teacher.assistant_courses` | 강사가 보조 강사로 참여하는 강좌 정보 | M:N |

> **M:N은 정참조와 역참조의 구분이 흐릿하다** — N:1에서는 외래 키를 가진 쪽이 참조, 반대가 역참조로 뚜렷이 갈렸다. M:N은 중개 테이블이 양쪽을 대칭으로 가리키므로 `course.assistant_teachers`와 `teacher.assistant_courses`가 **동등한 양방향 접근**이다. 어느 쪽에 필드를 선언했는지만 이름에 반영된다.

---

## ManyToManyField의 대표 인자 3가지

p.96에서 세 가지를 꼽는다.

1. `related_name`
2. `symmetrical`
3. `through`

### 1. `related_name` (p.97)

**역참조 시 사용하는 manager name을 변경한다.**

```python
class Patient(models.Model):
    doctors = models.ManyToManyField(Doctor, related_name='patients')
    name = models.TextField()
```

| | 코드 |
|---|---|
| 변경 전 | `doctor.patient_set.all()` |
| 변경 후 | `doctor.patients.all()` |

이름이 읽기 좋아지는 것도 있지만, 앞에서 본 것처럼 **같은 모델 쌍에 관계가 둘 이상일 때는 필수**가 된다.

### 2. `symmetrical` (p.98-99)

**관계 설정 시 대칭 유무 설정.** `ManyToManyField`가 **동일한 모델을 가리키는 정의에서만** 사용한다. 기본값은 `True`.

```python
# 예시
class Person(models.Model):
    friends = models.ManyToManyField('self')
    # friends = models.ManyToManyField('self', symmetrical=False)
```

| 값 | 동작 |
|---|---|
| `True` (기본) | source 모델의 인스턴스가 target 모델의 인스턴스를 참조하면, 자동으로 target 모델 인스턴스도 source 모델 인스턴스를 참조하도록 함 (대칭) |
| `False` | `True`의 반대 (대칭되지 않음) |

- **source 모델** — 관계를 시작하는 모델
- **target 모델** — 관계의 대상이 되는 모델

쉬운 비유로는 이렇다.

> 즉, 내가 당신의 친구라면 자동으로 당신도 내 친구가 됨

> **친구 관계와 팔로우 관계의 차이로 외우기** — 친구는 한쪽이 맺으면 양쪽이 성립하므로 `symmetrical=True`, 팔로우는 내가 팔로우해도 상대가 나를 팔로우하는 건 아니므로 `symmetrical=False`다. `'self'`를 참조할 때만 의미가 있는 인자라는 점도 함께 기억한다.

### 3. `through` (p.100)

**사용하고자 하는 중개 모델을 지정한다.** 일반적으로 **추가 데이터를 M:N 관계와 연결하려는 경우**에 활용한다.

```python
class Patient(models.Model):
    doctors = models.ManyToManyField(Doctor, through='Reservation')


class Reservation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom = models.TextField()
    reserved_at = models.DateTimeField(auto_now_add=True)
```

자동 생성되는 중개 테이블은 외래 키 두 개만 갖는다. 하지만 "환자와 의사가 연결됐다"는 사실 외에 **증상(`symptom`)과 예약 시각(`reserved_at`)** 처럼 **관계 자체에 딸린 정보**가 필요하면 자동 테이블로는 담을 수 없다. 그럴 때 중개 모델을 직접 정의하고 `through`로 지정한다.

> **`through`를 쓰면 `add()`/`remove()`가 제한된다** — 중개 모델에 필수 필드가 있으면 그 값 없이 관계만 만들 수 없기 때문이다. 이 경우 중개 모델의 인스턴스를 직접 생성하는 방식으로 관계를 맺는다.

---

## M:N에서의 대표 메서드

p.101에서 두 가지를 다룬다.

| 메서드 | 동작 |
|---|---|
| `add()` | 지정된 객체를 관련 객체 집합에 추가 |
| `remove()` | 관련 객체 집합에서 지정된 모델 객체를 제거 |

`add()`에는 중요한 성질이 하나 붙는다.

> 이미 존재하는 관계에 사용하면 **관계가 복제되지 않음**

같은 조합을 두 번 `add()` 해도 중개 테이블에 행이 두 개 생기지 않는다. 중복 체크를 직접 하지 않아도 되므로, 토글 기능을 만들 때 편하다. 실제 사용 예는 4편에서 다룬다.

```python
course.assistant_teachers.add(teacher)     # 관계 추가
course.assistant_teachers.remove(teacher)  # 관계 제거
```

---

## 정리 체크리스트

- [ ] M:N이 "양쪽 모두에서 N:1"이라는 말의 뜻을 설명할 수 있다
- [ ] 중개 테이블이 필요한 이유를 컬럼 구조로 설명할 수 있다
- [ ] `ManyToManyField` 추가만으로 migration이 깨지는 원인을 안다
- [ ] `related_name`이 선택이 아니라 필수가 되는 상황을 말할 수 있다
- [ ] Teacher–Course 사이 네 가지 접근 경로를 각각 쓸 수 있다
- [ ] `symmetrical`이 `'self'` 참조에서만 의미 있는 이유를 안다
- [ ] `through`를 언제 쓰는지 한 문장으로 말할 수 있다
- [ ] `add()`를 두 번 호출하면 어떻게 되는지 안다

## 복습 문제

1. M:N에서 외래 키를 어느 한쪽 테이블에 둘 수 없는 이유는?
   <details><summary>답</summary>외래 키는 대상이 항상 하나일 때만 컬럼 하나로 표현된다. M:N은 양쪽 다 여러 개라 어느 쪽에 두든 값이 여러 개 필요해진다. 그래서 관계를 저장하는 제3의 중개 테이블이 필요하다.</details>

2. `assistant_teachers = models.ManyToManyField(Teacher)`만 추가했는데 migration이 실패한 이유는?
   <details><summary>답</summary>이 필드가 만드는 역참조 매니저 이름이 `course_set`인데, 기존 `main_teacher` N:1 관계가 이미 `teacher.course_set`을 쓰고 있다. 두 관계가 같은 이름을 요구해 충돌한다. 둘 중 하나에 `related_name`을 지정해야 한다.</details>

3. 중개 테이블 `courses_course_assistant_teachers`의 컬럼 구성은?
   <details><summary>답</summary>`id`(PK), `course_id`(Course 외래 키), `teacher_id`(Teacher 외래 키) 세 개다. 관계를 나타내는 외래 키 두 개가 전부다.</details>

4. `symmetrical=False`는 어떤 상황에서 쓰는가?
   <details><summary>답</summary>같은 모델을 참조하는 M:N에서 관계가 한쪽 방향으로만 성립해야 할 때다. 팔로우처럼 내가 상대를 참조해도 상대가 나를 참조하지는 않는 관계가 예다. 기본값 `True`는 친구 관계처럼 자동 대칭이 된다.</details>

5. 자동 생성 중개 테이블 대신 `through`로 직접 모델을 지정하는 경우는?
   <details><summary>답</summary>관계 자체에 딸린 추가 데이터를 저장해야 할 때다. 예약 관계에서 증상이나 예약 시각처럼, 두 모델 어느 쪽에도 속하지 않고 "연결"에 속하는 정보가 있으면 중개 모델을 직접 정의한다.</details>

6. 이미 연결된 강사에게 `add()`를 다시 호출하면?
   <details><summary>답</summary>아무 일도 일어나지 않는다. 이미 존재하는 관계에 `add()`를 사용해도 관계가 복제되지 않으므로 중개 테이블에 중복 행이 생기지 않는다.</details>
