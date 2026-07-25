# Fundamentals of HTML and CSS

> SSAFY 16기 데이터트랙 · 2026-07-20 강의자료 정리 (총 143p)

## 목차

1. [웹 기초](#1-웹-기초)
2. [웹 구조화 — HTML](#2-웹-구조화--html)
3. [웹 스타일링 — CSS 기초](#3-웹-스타일링--css-기초)
4. [CSS 선택자 (Selectors)](#4-css-선택자-selectors)
5. [명시도와 Cascade](#5-명시도specificity와-cascade)
6. [CSS Box Model](#6-css-box-model)
7. [Box Type (display)](#7-box-typedisplay)
8. [CSS Position](#8-css-position)
9. [z-index](#9-z-index)
10. [CSS 프레임워크 — Bootstrap](#10-css-프레임워크--bootstrap)

---

## 1. 웹 기초

### World Wide Web
인터넷으로 연결된 컴퓨터들이 정보를 공유하는 거대한 정보 공간

### Web page 구성 요소

| 기술 | 역할 | 키워드 |
|---|---|---|
| **HTML** | 구조 | Structure |
| **CSS** | 스타일 | Styling |
| **JavaScript** | 동작 | Behavior |

---

## 2. 웹 구조화 — HTML

### HTML이란
**H**yper**T**ext **M**arkup **L**anguage
→ 웹 페이지의 **의미**와 **구조**를 정의하는 언어

**Hypertext**
- 웹 페이지를 다른 페이지로 연결하는 링크
- 참조를 통해 사용자가 한 문서에서 다른 문서로 즉시 접근할 수 있는 텍스트

**Markup Language**
- 태그 등을 이용하여 문서나 데이터의 구조를 명시하는 언어
- ex) HTML, Markdown

> 💡 참고: Hyper Text는 인간이 기억하는 방식까지 바꾸고 있으며, 컬럼비아대 벳시 스패로 교수팀은 이를 **구글 효과(Google Effect)** 라고 명명해 『사이언스』지에 게재

### HTML 기본 구조

| 태그 | 설명 |
|---|---|
| `<!DOCTYPE html>` | 해당 문서가 html로 문서라는 것을 나타냄 |
| `<html></html>` | 전체 페이지의 콘텐츠를 포함 |
| `<head></head>` | HTML 문서에 관련된 설명, 설정 등 (사용자에게 보이지 않음) |
| `<body></body>` | 페이지에 표시되는 모든 콘텐츠 |

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My page</title>
</head>
<body>
  <p>This is my page</p>
</body>
</html>
```

### HTML Element (요소)

```
Opening tag                     Closing tag
    ↓                                ↓
  <p>My cat is very grumpy</p>
     └────── Content ──────┘
  └────────── Element ─────────┘
```

- 하나의 요소는 **여는 태그 + 내용 + 닫는 태그**로 구성됨
- 닫는 태그는 태그 이름 앞에 슬래시가 포함되며, **닫는 태그가 없는 태그**도 존재 (`<img>`, `<meta>` 등)

### HTML Attributes (속성)

```html
<p class="editor-note">My cat is very grumpy</p>
       └─ Attribute ─┘
```

**규칙**
- 속성은 요소 이름과 속성 사이에 공백이 있어야 함
- 하나 이상의 속성들이 있는 경우엔 속성 사이에 공백으로 구분함
- 속성 값은 열고 닫는 따옴표로 감싸야 함

**목적**
- 나타내고 싶지 않지만 **추가적인 기능·내용**을 담고 싶을 때 사용
- CSS에서 해당 **요소를 선택**하기 위한 값으로 활용됨

### HTML 구조 예시

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My page</title>
</head>
<body>
  <p>My page</p>
  <a href="https://www.google.co.kr/">Google</a>
  <img src="images/sample.png" alt="sample-img">
  <img src="https://random.imagecdn.app/500/150/" alt="sample-img">
</body>
</html>
```

### HTML Text Structure

HTML의 주요 목적 중 하나는 **텍스트 구조와 의미**를 제공하는 것

> `<h1>Heading</h1>`
> 예를 들어 h1 요소는 단순히 텍스트를 크게만 만드는 것이 아닌, 현재 **문서의 최상위 제목**이라는 의미를 부여하는 것

**대표적인 Text structure 태그**

| 분류 | 태그 |
|---|---|
| Heading & Paragraphs | `h1`~`h6`, `p` |
| Lists | `ol`, `ul`, `li` |
| Emphasis & Importance | `em`, `strong` |

```html
<body>
  <h1>Main Heading</h1>
  <h2>Sub Heading</h2>
  <p>This is my page</p>
  <p>This is <em>emphasis</em></p>
  <p>Hi <strong>my name</strong> is Air</p>
  <ol>
    <li>파이썬</li>
    <li>알고리즘</li>
    <li>웹</li>
  </ol>
</body>
```

### 📌 참고 — HTML 관련 사항

- 요소(태그) 이름은 대소문자를 구분하지 않지만 **"소문자"** 사용을 권장
- 속성의 따옴표는 작은따옴표와 큰따옴표를 구분하지 않지만 **"큰따옴표"** 권장
- HTML은 프로그래밍 언어와 달리 **에러를 반환하지 않기 때문에** 작성 시 주의

---

## 3. 웹 스타일링 — CSS 기초

### CSS란
**C**ascading **S**tyle **S**heet
→ 웹 페이지의 **디자인과 레이아웃**을 구성하는 언어

### CSS 구문

```css
h1 {                  /* 선택자 (Selector) */
  color: red;         /* 선언 (Declaration) */
  font-size: 30px;    /* 속성(Property): 값(Value) */
}
```

| 구성 | 설명 |
|---|---|
| 선택자 (Selector) | 스타일을 적용할 대상 |
| 선언 (Declaration) | `속성: 값;` 한 쌍 |
| 속성 (Property) | 바꾸고 싶은 스타일 항목 |
| 값 (Value) | 적용할 값 |

### CSS 적용 방법 3가지

#### 1) 인라인(Inline) 스타일
HTML 요소 안에 `style` 속성 값으로 작성

```html
<body>
  <h1 style="color: blue; background-color: yellow;">Inline Style</h1>
</body>
```

#### 2) 내부(Internal) 스타일 시트
`head` 태그 안 `style` 태그에 작성

```html
<head>
  <title>Document</title>
  <style>
    h2 {
      color: red;
    }
  </style>
</head>
```

#### 3) 외부(External) 스타일 시트
별도의 CSS 파일 생성 후 `link` 태그로 연결

```html
<head>
  <link rel="stylesheet" href="style.css">
  <title>Document</title>
</head>
```

---

## 4. CSS 선택자 (Selectors)

HTML 요소를 선택하여 스타일을 적용할 수 있도록 하는 선택자

### 종류

**기본 선택자**
- 전체(`*`) 선택자
- 요소(tag) 선택자
- 클래스(class) 선택자
- 아이디(id) 선택자
- 속성(attr) 선택자 등

**결합자 (Combinators)**
- 자손 결합자 `" "` (space)
- 자식 결합자 `">"`

### 특징 정리

| 선택자 | 기호 | 설명 |
|---|---|---|
| 전체 선택자 | `*` | HTML 모든 요소를 선택 |
| 요소 선택자 | `tag` | 지정한 모든 태그를 선택 |
| 클래스 선택자 | `.` (dot) | 주어진 클래스 속성을 가진 **모든 요소**를 선택 |
| 아이디 선택자 | `#` | 주어진 아이디 속성을 가진 요소 선택 (문서에 **하나만** 존재해야 함) |
| 자손 결합자 | `" "` (space) | 첫 번째 요소의 **자손 요소들** 선택 (하위 레벨 상관 없이)<br>예) `p span` → `<p>` 안의 모든 `<span>` |
| 자식 결합자 | `">"` | 첫 번째 요소의 **직계 자식**만 선택 (한 단계 아래만)<br>예) `ul > li` → `<ul>` 안의 모든 `<li>` |

### 예시

```html
<body>
  <h1 class="green">Heading</h1>
  <h2>선택자 연습</h2>
  <h3>Hello</h3>
  <h4>Nice to meet you</h4>
  <p id="purple">과목 목록</p>
  <ul class="green">
    <li>파이썬</li>
    <li>알고리즘</li>
    <li>웹
      <ol>
        <li>HTML</li>
        <li>CSS</li>
        <li>PYTHON</li>
      </ol>
    </li>
  </ul>
  <p class="green">Lorem, <span>ipsum</span> dolor.</p>
</body>
```

```css
/* 전체 선택자 */
* { color: red; }

/* 타입(요소) 선택자 */
h2 { color: orange; }
h3, h4 { color: blue; }

/* 클래스 선택자 */
.green { color: green; }

/* id 선택자 */
#purple { color: purple; }

/* 자식 결합자 */
.green > span { font-size: 50px; }

/* 자손 결합자 */
.green li { color: brown; }
```

### 📌 참고 — CSS의 모든 속성을 외우는 것이 아님

- 자주 사용되는 속성은 그리 많지 않으며, 주로 활용하는 속성 위주로 사용하다 보면 자연스럽게 익히게 됨
- 그 외 속성들은 개발하며 필요할 때마다 **검색해서 학습 후 사용**할 것

---

## 5. 명시도(Specificity)와 Cascade

### Specificity (명시도)
> 결과적으로 요소에 적용할 CSS 선언을 결정하기 위한 알고리즘

- CSS Selector에 **가중치**를 계산하여 어떤 스타일을 적용할지 결정
- 동일한 요소를 가리키는 2개 이상의 CSS 규칙이 있는 경우, **가장 높은 명시도를 가진 Selector가 승리**하여 스타일이 적용됨

### Cascade (계단식)
> 한 요소에 **동일한 가중치**를 가진 선택자가 적용될 때, CSS에서 **마지막에 나오는 선언**이 사용됨

```css
h1 { color: red; }
h1 { color: purple; }   /* ✅ 최종 적용 */
```

### 명시도가 높은 순 ⭐

1. **Importance** — `!important`
2. **Inline 스타일**
3. **선택자** — `id 선택자` > `class 선택자` > `요소 선택자`
4. **소스 코드 선언 순서**

```css
/* 동일한 h1 태그에 다음과 같이 스타일이 작성된다면 → red 적용 */
.make-red { color: red; }    /* ✅ class > 요소 */
h1 { color: purple; }
```

### `!important`
> 다른 우선순위 규칙보다 우선하여 적용하는 키워드

❗ Cascade의 구조를 무시하고 강제로 스타일을 적용하는 방식이므로 **사용을 권장하지 않음**

### 📌 참고 — 명시도 관련 문서

- 그림으로 보는 명시도: https://specifishity.com/
- 명시도 계산기: https://specificity.keegan.st/

---

## 6. CSS Box Model

> 모든 HTML 요소를 **사각형 박스**로 표현하는 개념
> 내용(content), 안쪽 여백(padding), 테두리(border), 외부 간격(margin)으로 구성

> 💡 "원은 네모 박스를 깎은 것" — 개발자 도구로 보면 원형 요소도 사각형 박스

### Box 구성 요소

```
┌──────────── margin ────────────┐
│  ┌────────  border  ────────┐  │
│  │  ┌──── padding ────┐     │  │
│  │  │    content      │     │  │
│  │  └─────────────────┘     │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

| 영역 | 설명 |
|---|---|
| **Content** | 콘텐츠가 표시되는 영역 |
| **Padding** | 콘텐츠 주위에 위치하는 공백 영역 |
| **Border** | 콘텐츠와 패딩을 감싸는 테두리 영역 |
| **Margin** | 이 박스와 다른 요소 사이의 공백, 가장 바깥쪽 영역 |

**방향별 명칭**: `margin-top/right/bottom/left`, `border-*`, `padding-*` 각각 지정 가능

### Box 구성 요소 예시

```css
.box1 {
  width: 200px;
  padding-left: 25px;
  padding-bottom: 25px;
  margin-left: 25px;
  margin-top: 50px;
  border-width: 3px;
  border-style: solid;
  border-color: black;
}

.box2 {
  width: 200px;
  padding: 25px 50px;
  margin: 25px auto;
  border: 1px dashed black;
}
```

### width & height 속성

- 요소의 너비와 높이를 지정
- 이때 지정되는 요소의 너비와 높이는 **콘텐츠 영역**을 대상으로 함

❗ `width: 200px`라고 해도 **실제 박스 너비는 200px이 아니다**
→ CSS는 border가 아닌 **content의 크기**를 width 값으로 지정하기 때문

### box-sizing 속성 ⭐

```css
/* 기본값: width = content만 */
* { box-sizing: content-box; }

/* width = content + padding + border */
* { box-sizing: border-box; }
```

| 값 | width가 포함하는 범위 |
|---|---|
| `content-box` (기본값) | content |
| `border-box` | content + padding + border |

```css
.box {
  width: 100px;
  border: 2px solid black;
  padding: 10px;
  margin: 20px;
  background-color: lightyellow;
}
.content-box { box-sizing: content-box; }
.border-box  { box-sizing: border-box; }
```

### 📌 참고 — shorthand 속성

**`border`** — `border-width`, `border-style`, `border-color`를 한번에 설정

```css
/* 작성 순서는 영향을 주지 않음 */
border: 2px solid black;
```

**`margin` & `padding`** — 4방향의 속성을 한번에 지정

```css
/* 4개 - 상우하좌 */
margin:  10px 20px 30px 40px;
padding: 10px 20px 30px 40px;

/* 3개 - 상/좌우/하 */
margin:  10px 20px 30px;
padding: 10px 20px 30px;

/* 2개 - 상하/좌우 */
margin:  10px 20px;
padding: 10px 20px;

/* 1개 - 공통 */
margin:  10px;
padding: 10px;
```

### 📌 참고 — Margin collapsing (마진 상쇄)

- 두 block 타입 요소의 margin `top`과 `bottom`이 만나 **더 큰 margin으로 결합**되는 현상
- 웹 개발자가 레이아웃을 더욱 쉽게 관리할 수 있도록 함
- 각 요소에 대한 상/하 margin을 각각 설정하지 않고 한 요소에 대해서만 설정하기 위함

> 예) 두 요소 모두 `margin: 20px`이지만 실제 두 요소의 상/하 여백은 40이 아닌 **20**으로 상쇄
> 참고: [MDN — Mastering margin collapsing](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Box_Model/Mastering_margin_collapsing)

---

## 7. Box Type(display)

### Normal flow
CSS를 적용하지 않았을 경우 웹페이지 요소가 기본적으로 배치되는 방향
- **Block Direction** (수직) / **Inline Direction** (수평)

### block 타입 특징

```css
.index { display: block; }
```

- 항상 **새로운 행**으로 나뉨
- `width`와 `height` 속성을 사용하여 너비와 높이를 지정할 수 있음
- 기본적으로 `width` 속성을 지정하지 않으면 박스는 inline 방향으로 **사용 가능한 공간을 모두 차지함** (너비를 사용가능한 공간의 100%로 채우는 것)
- 대표적인 block 타입 태그 — `h1`~`h6`, `p`, `div`

### inline 타입 특징

```css
.index { display: inline; }
```

- 새로운 행으로 나뉘지 않음
- `width`와 `height` 속성을 **사용할 수 없음**
- **수직 방향** — `padding`, `margins`, `borders`가 적용되지만 다른 요소를 밀어낼 수는 **없음**
- **수평 방향** — `padding`, `margins`, `borders`가 적용되어 다른 요소를 밀어낼 수 **있음**
- 대표적인 inline 타입 태그 — `a`, `img`, `span`

### 속성에 따른 수평 정렬

| 방법 | 효과 |
|---|---|
| `margin-right: auto;` | 왼쪽 정렬 |
| `margin-left: auto;` | 오른쪽 정렬 |
| `margin-left: auto; margin-right: auto;` | 가운데 정렬 (박스 자체) |
| `text-align: left / right / center;` | 내부 인라인 콘텐츠 정렬 |

### `inline-block`

- inline과 block 요소 사이의 **중간 지점**을 제공하는 display 값
- block 요소의 특징을 가짐
  - `width` 및 `height` 속성 사용 가능
  - `padding`, `margin` 및 `border`로 인해 다른 요소가 밀려남
- ➡️ **요소가 줄 바꿈 되는 것을 원하지 않으면서 너비와 높이를 적용하고 싶은 경우**에 사용

```css
span {
  margin: 20px;
  padding: 20px;
  width: 80px;
  height: 50px;
  background-color: lightblue;
  border: 2px solid blue;
  display: inline-block;
}

ul > li {
  background-color: crimson;
  padding: 10px 20px;
  display: inline-block;
}

.container { text-align: center; }
.box {
  display: inline-block;
  width: 100px;
  height: 100px;
  background-color: #4CAF50;
  margin: 10px;
}
```

### `flex`

- 요소를 **행과 열 형태**로 배치하는 **1차원 레이아웃** 방식
- ➡️ '공간 배열' & '정렬'

| 구분 | 속성 |
|---|---|
| Flex Container | `display`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`, `align-content` |
| Flex Item | `align-self`, `flex-grow`, `flex-basis`, `order` |

```css
.container {
  height: 500px;
  border: 1px solid black;
  display: flex;    /* ← */
}
```

- flex item은 기본적으로 **행**(주 축의 기본값인 가로 방향)으로 나열
- flex item은 **주 축의 시작 선**에서 시작
- flex item은 **교차 축의 크기를 채우기 위해 늘어남**

### `none`

- 요소를 화면에 표시하지 않고, **공간조차 부여되지 않음**

```css
.box {
  width: 100px;
  height: 100px;
  background-color: red;
  border: 2px solid black;
}
.none { display: none; }
```

---

## 8. CSS Position

> 요소를 **Normal Flow에서 제거**하여 다른 위치로 배치하는 것
> ➡️ 다른 요소 위에 올리기, 화면의 특정 위치에 고정시키기 등

### Position 이동 방향
`top` / `right` / `bottom` / `left` + **Z Axis** (`z-index`)

### Position 유형 ⭐

| 값 | Normal Flow | 이동 기준 | 문서 내 공간 |
|---|---|---|---|
| `static` | 따라 배치 (기본값) | — | 차지함 |
| `relative` | 따라 배치 | **자기 자신** | static일 때와 **같음** |
| `absolute` | **제거** | 가장 가까운 **relative 부모 요소** | **없어짐** |
| `fixed` | **제거** | 현재 **화면영역(viewport)** | **없어짐** |
| `sticky` | 따라 배치 | 스크롤 임계점 | 차지함 |

**`sticky` 상세**
- 요소가 일반적인 문서 흐름에 따라 배치되다가 **스크롤이 특정 임계점에 도달하면 그 위치에서 고정됨**(fixed)
- 만약 다음 sticky 요소가 나오면 다음 sticky 요소가 이전 sticky 요소의 자리를 대체
- 이전 sticky 요소가 고정되어 있던 위치와 다음 sticky 요소가 고정되어야 할 위치가 겹치게 되기 때문

### Position 예시

```css
* { box-sizing: border-box; }
body { height: 1500px; }

.container {
  position: relative;
  height: 300px;
  width: 300px;
  border: 1px solid black;
}
.box {
  height: 100px;
  width: 100px;
  border: 1px solid black;
}

.static {
  position: static;
  background-color: lightcoral;
}
.absolute {
  position: absolute;
  background-color: lightgreen;
  top: 100px;
  left: 100px;
}
.relative {
  position: relative;
  background-color: lightblue;
  top: 100px;
  left: 100px;
}
.fixed {
  position: fixed;
  background-color: gray;
  bottom: 0;
  right: 0;
}
```

### sticky 예시

```css
body { height: 1500px; }

.sticky {
  position: sticky;
  top: 0;
  background-color: lightblue;
  padding: 20px;
  border: 2px solid black;
}
```

### 실제 사용 예시

| 사례 | position | 설명 |
|---|---|---|
| 네이버 배지 아이콘 | `absolute` | Normal flow에서 벗어나 부모를 기준으로 좌측 상단 모서리로 이동 |
| 우측 하단 플로팅 버튼 | `fixed` | Normal flow에서 벗어나 화면을 기준으로 우측 하단에 위치 |
| 에어비앤비 검색 필터 바 | `sticky` | 임계점에 도달한 이후 고정됨 |

### absolute 예시 — 카드 배지

```html
<div class="card">
  <div class="card-content">
    <h3>Card Title</h3>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    <span class="badge">New</span>
  </div>
</div>
```

```css
.card {
  position: relative;     /* 기준점 */
  width: 300px;
  height: 200px;
  border: 1px solid black;
}
.card-content { padding: 10px; }
.badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: red;
  color: white;
  padding: 5px 10px;
}
```

### 📌 참고 — CSS 상속

CSS는 부모 요소의 속성을 자식이 물려받지만, **상속되지 않는 속성**도 있음

- Box model 관련 요소 — `width`, `height`, `border`, `box-sizing` …
- position 관련 요소 — `position`, `top`/`right`/`bottom`/`left`, `z-index` 등

```html
<ul class="parent">
  <li class="child">Hello</li>
  <li class="child">Bye</li>
</ul>
```

> MDN 각 속성 문서의 **Formal definition** 표에서 상속 여부 확인 가능

---

## 9. z-index

- 요소의 **쌓임 순서(stack order)** 를 정의
- 값이 클수록 앞(위)에 배치됨
- `position` 속성이 `static`이 아닌 요소에만 적용

```html
<div class="container">
  <div class="box red"></div>
  <div class="box green"></div>
  <div class="box blue"></div>
</div>
```

```css
.container { position: relative; }

.box {
  position: absolute;
  width: 100px;
  height: 100px;
}

.red {
  background-color: red;
  top: 50px; left: 50px;
  z-index: 3;      /* 가장 앞 */
}
.green {
  background-color: green;
  top: 100px; left: 100px;
  z-index: 2;
}
.blue {
  background-color: blue;
  top: 150px; left: 150px;
  z-index: 1;      /* 가장 뒤 */
}
```

---

## 10. CSS 프레임워크 — Bootstrap

### Bootstrap
> The world's most popular front-end open source toolkit
> (gitstar-ranking 상위권 오픈소스)

### 사용해보기

1. Bootstrap 공식 문서 접속 — https://getbootstrap.com
2. `Docs → Introduction → Quick start`
3. **"Include Bootstrap's CSS and JS"** 코드 확인 및 가져오기
4. `head`와 `body`에 bootstrap CDN이 포함된 코드 블록 삽입

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bootstrap demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
          rel="stylesheet" crossorigin="anonymous">
  </head>
  <body>
    <h1>Hello, world!</h1>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"
            crossorigin="anonymous"></script>
  </body>
</html>
```

### 기본 사용법 — 유틸리티 클래스

```html
<h1 class="mt-5">Hello, world!</h1>
```

**작명 규칙**

```
{property}{sides}-{size}
```

| 구분 | 예시 값 |
|---|---|
| property | `m` (margin), `p` (padding) |
| sides | `t`(top), `b`(bottom), `s`(start/left), `e`(end/right), `x`(좌우), `y`(상하), 생략(전체) |
| size | `0` ~ `5`, `auto` |

> 예) `mt-5` → margin-top 5단계

---

## ✅ 핵심 요약

| 주제 | 꼭 기억할 것 |
|---|---|
| HTML | 구조·의미 부여. 태그+속성. 에러를 반환하지 않으니 주의 |
| CSS 적용 | Inline / Internal / **External(권장)** |
| 선택자 | `*`, `tag`, `.class`, `#id` + 자손( ` ` ) / 자식( `>` ) |
| 명시도 | `!important` > inline > id > class > 요소 > **선언 순서** |
| Box Model | content + padding + border + margin |
| box-sizing | 실무에선 `* { box-sizing: border-box; }` 를 자주 사용 |
| display | block / inline / inline-block / flex / none |
| position | static · relative(자기 기준) · absolute(relative 부모 기준) · fixed(viewport) · sticky(스크롤 임계점) |
| z-index | 숫자 클수록 위. static이 아닌 요소에만 적용 |
