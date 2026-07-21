# DOM & Event 정리 (SSAFY 16기 데이터트랙 · 0721)

> JavaScript 기초(변수 → 데이터 타입 → 연산자 → 제어문 → 함수) → DOM → Event 순서로 진행된 강의 정리.
> ✚ 표시는 강의에 없지만 알아두면 좋은 보충 내용.

---

## 1. History of JavaScript

### ECMAScript와 JavaScript
- **ECMAScript**: Ecma International이 정의하는 표준화된 스크립트 언어 **명세(스펙)**
- **JavaScript**: ECMAScript 표준을 따라 구현된 **구체적인 언어** (브라우저, Node.js 등에서 실행)
- 정리: ECMAScript는 표준, JavaScript는 그 표준의 구현체

### 주요 버전
- **ES5 (2009)**: 안정성과 생산성 크게 향상
- **ES6 / ECMAScript 2015**: 객체지향 언어로서 큰 발전, 역사상 가장 중요한 버전으로 평가 (`let`/`const`, 화살표 함수, 템플릿 리터럴, spread 등 대부분 여기서 추가)
- 현재: 브라우저 페이지의 동적 기능 구현을 넘어 서버(Node.js), 모바일 등 다양한 환경에서 사용

---

## 2. 변수

### 식별자 네이밍 규칙
- 문자, `$`, `_`로 시작 / 대소문자 구분 / 예약어(`for`, `if`, `function` 등) 사용 불가

### Naming case
| 케이스 | 용도 | 예시 |
|---|---|---|
| camelCase | 변수, 객체, 함수 | `userName` |
| PascalCase | 클래스, 생성자 | `UserProfile` |
| SNAKE_CASE (대문자) | 상수 | `MAX_COUNT` |

### 변수 선언 키워드 — `let` / `const` (ES6 추가)
- **`let`**: 재할당 ⭕ / 재선언 ❌ / 블록 스코프
- **`const`**: 재할당 ❌ / 재선언 ❌ / 블록 스코프 / **선언 시 반드시 초기값 필요**

```javascript
const number = 10
number = 10        // TypeError: Assignment to constant variable
const number = 20  // SyntaxError: 이미 선언됨
const number       // SyntaxError: 초기값 없음
```

### 블록 스코프 (block scope)
- `if`, `for`, 함수 등의 중괄호 `{}` 내부에서 선언된 변수는 블록 밖에서 접근 불가

```javascript
let x = 1
if (x === 1) {
  let x = 2
  console.log(x)  // 2
}
console.log(x)    // 1
```

### 어떤 키워드를 쓸까
- **기본적으로 `const` 사용 권장**, 재할당이 필요해지면 그때 `let`으로 변경

### (참고) `var`를 쓰지 않는 이유
- ES6 이전의 키워드. **재선언/재할당 모두 가능**, **함수 스코프(function scope)**
- **호이스팅(hoisting)** 되는 특성으로 예기치 못한 문제 발생 가능 → `const`/`let` 사용 권장

```javascript
console.log(name)     // undefined (에러 아님! var 호이스팅)
var name = '홍길동'

console.log(age)      // ReferenceError (let은 TDZ)
let age = 30
```

> ✚ **보충 — TDZ(Temporal Dead Zone)**: `let`/`const`도 사실 호이스팅은 되지만, 선언문 이전 구간(TDZ)에서 접근하면 ReferenceError가 발생하도록 설계됨. "호이스팅이 안 된다"보다 "접근이 막힌다"가 정확한 이해.

---

## 3. 데이터 타입

### 원시 자료형 vs 참조 자료형
| | 원시 (Primitive) | 참조 (Reference) |
|---|---|---|
| 종류 | Number, String, Boolean, null, undefined | Object, Array, Function |
| 저장 방식 | 변수에 **값이 직접** 저장 | 객체의 **주소**가 저장 |
| 특징 | 불변, **값이 복사** | 가변, **주소가 복사** |

```javascript
// 원시: 값 복사
let a = 10
let b = a
b = 20
console.log(a, b)  // 10 20

// 참조: 주소 복사
const obj1 = { name: 'Alice', age: 30 }
const obj2 = obj1
obj2.age = 40
console.log(obj1.age)  // 40 (같이 바뀜!)
```

### Number
- 정수/실수 구분 없는 하나의 숫자 타입
- 특수 값: `Infinity`, `-Infinity`, `NaN` (Not a Number)
- NaN이 되는 경우: `Number(undefined)`, `Math.sqrt(-1)`, `7 ** NaN`, `0 * Infinity` 등

### String
- `+` 연산자로 연결 가능
- **Template literals** (ES6): 백틱과 `${}` 로 표현식 삽입

```javascript
const age = 100
const message = `홍길동은 ${age}세입니다.`
```

### null과 undefined
| | null | undefined |
|---|---|---|
| 의미 | 값이 없음을 **의도적으로** 표현 | 선언 후 값을 할당하지 않으면 **자동으로** 할당 |

> ✚ **보충**: `typeof null === 'object'`는 JS 초기 설계 버그(하위 호환 때문에 못 고침). 면접/시험 단골.

### Boolean과 자동 형변환 (ToBoolean)
조건문·반복문에서 Boolean이 아닌 값은 자동으로 참/거짓 변환됨.

| 데이터 타입 | false | true |
|---|---|---|
| undefined | 항상 false | — |
| null | 항상 false | — |
| Number | `0`, `-0`, `NaN` | 나머지 모든 경우 |
| String | `''` (빈 문자열) | 나머지 모든 경우 |

> ✚ **보충**: false가 되는 값들을 **falsy** (`false`, `0`, `-0`, `NaN`, `''`, `null`, `undefined`), 나머지를 **truthy**라고 부름. `[]`(빈 배열)와 `{}`(빈 객체)는 **truthy**라는 점 주의 — 파이썬과 다름!

---

## 4. 연산자

### 할당 연산자
```javascript
let a = 3
a += 10   // 13
a -= 3    // 10
a *= 10   // 100
a %= 7    // 2
```

### 비교 연산자
- 피연산자를 비교해 boolean 반환 (`<`, `>`, `<=`, `>=`)

### 동등(`==`) vs 일치(`===`)
```javascript
console.log(1 == '1')     // true  (암묵적 형변환 후 비교)
console.log(0 == false)   // true

console.log(1 === '1')    // false (타입까지 비교)
console.log(0 === false)  // false
```
- **`===` 사용을 권장** (예측 가능, 버그 예방)

### 논리 연산자
- `&&`(and), `||`(or), `!`(not) — 단축 평가(short-circuit) 동작

---

## 5. 조건문 & 삼항 연산자

### if / else if / else
- 조건은 소괄호, 실행 코드는 중괄호 블록

### 삼항 연산자
```javascript
condition ? expression1 : expression2

const message = age >= 20 ? '성인' : '미성년자'
```
- 간단한 조건 분기에서 코드를 짧게 표현. 중첩은 가독성이 나빠지므로 지양

---

## 6. 반복문

### while
```javascript
let i = 0
while (i < 6) {
  console.log(i)
  i += 1
}
```

### for
```javascript
for (let i = 0; i < 6; i++) {
  console.log(i)
}
```
- 실행 순서: ① 초기화 → ② 조건 검사 → ③ 본문 실행 → ④ 증감 → ②로 반복

### for...in — **객체**의 속성(key) 순회
```javascript
const capitals = { korea: '서울', japan: '도쿄', china: '베이징' }
for (const capital in capitals) {
  console.log(capital)  // korea, japan, china (key)
}
```

### for...of — **반복 가능한 객체**(배열, 문자열 등)의 값 순회
```javascript
const numbers = [0, 1, 2, 3]
for (const number of numbers) {
  console.log(number)  // 0, 1, 2, 3 (값)
}
```

### for...in을 배열에 쓰면 안 되는 이유
- 배열에 `for...in`을 쓰면 값이 아닌 **인덱스(문자열)** 가 반환됨
- 내부적으로 순서 보장이 안 되는 방식이라, **인덱스 순서가 중요한 배열에서는 사용 금지**
- 정리: **객체 → `for...in`, 배열 → `for` 또는 `for...of`**

### 반복문에서 const vs let
- `for (let i = 0; ...)`: `i`를 **재할당**하며 돌기 때문에 `const` 사용 시 에러
- `for...in` / `for...of`: 매 반복마다 새로 선언되므로 `const` 사용 가능

---

## 7. 함수

### 함수 구조
```javascript
function name(param1, param2) {
  // statements
  return value
}
```
- `return` 값이 없으면 **`undefined` 반환**

### 선언식 vs 표현식
| | 선언식 (declaration) | 표현식 (expression) |
|---|---|---|
| 형태 | `function add() {...}` | `const sub = function () {...}` |
| 특징 | 호이스팅 영향을 받음 | 변수 선언 규칙을 따름 |

```javascript
// 선언식
function add(num1, num2) {
  return num1 + num2
}

// 표현식 (익명 함수를 변수에 할당)
const sub = function (num1, num2) {
  return num1 - num2
}
```
> ✚ **보충**: 표현식이 권장되는 이유 — 호이스팅으로 인해 선언식은 "선언 전 호출"이 가능해져 코드 흐름 파악이 어려워짐. 표현식은 이런 문제가 없음.

### 매개변수

**1. 기본 함수 매개변수 (Default parameters)**
```javascript
const greeting = function (name = 'Anonymous') {
  return `Hi ${name}`
}
greeting()  // 'Hi Anonymous'
```

**2. 나머지 매개변수 (Rest parameters)**
```javascript
const myFunc = function (param1, param2, ...restParams) {
  return [param1, param2, restParams]
}
myFunc(1, 2, 3, 4, 5)  // [1, 2, [3, 4, 5]]
myFunc(1, 2)           // [1, 2, []]
```

**매개변수 개수 ≠ 인자 개수일 때 (에러 아님!)**
```javascript
// 매개변수 > 인자 → 누락된 건 undefined
const threeArgs = function (p1, p2, p3) { return [p1, p2, p3] }
threeArgs(1)     // [1, undefined, undefined]

// 매개변수 < 인자 → 초과분은 무시
const twoArgs = function (p1, p2) { return [p1, p2] }
twoArgs(1, 2, 3) // [1, 2]
```

### Spread syntax (`...`)
- 전개 대상에 따라 역할이 다름
  - **함수 호출 시**: 배열을 개별 인자로 펼침 → `myFunc(...numbers)`
  - **함수 정의 시**: 나머지 매개변수(모으기) → `(...restArgs)`

```javascript
function myFunc(x, y, z) { return x + y + z }
let numbers = [1, 2, 3]
console.log(myFunc(...numbers))  // 6
```
> ✚ **보충**: 배열/객체 복사에도 자주 씀 — `const copy = [...arr]`, `const merged = {...obj1, ...obj2}` (얕은 복사라는 점 주의)

### 화살표 함수 (Arrow function, ES6)
축약 단계:
```javascript
const arrow1 = function (name) { return `hello, ${name}` }

// 1. function 키워드 제거, => 추가
const arrow2 = (name) => { return `hello, ${name}` }

// 2. 매개변수가 1개면 () 생략 가능 (단, 생략하지 않는 것 권장)
const arrow3 = name => { return `hello, ${name}` }

// 3. 본문이 한 줄이면 {} 와 return 생략 가능
const arrow4 = name => `hello, ${name}`
```

**객체를 바로 반환할 때는 소괄호로 감싸기**
```javascript
const returnObject = () => ({ key: 'value' })  // ()가 없으면 {}를 블록으로 해석
```

### (참고) 세미콜론
- JS는 ASI(Automatic Semicolon Insertion, 자동 세미콜론 삽입) 규칙이 있어 생략 가능
- 이 강의는 세미콜론 없는 스타일 사용

---

## 8. DOM

### 웹 브라우저에서의 JavaScript
- 웹 페이지의 동적인 기능 구현
- 실행 환경 3가지: ① HTML `<script>` 태그 ② 외부 `.js` 파일 ③ 브라우저 Console

### DOM (The Document Object Model)
- 웹 페이지(Document)를 **구조화된 객체로 제공**하여, 프로그래밍 언어가 페이지 구조에 접근할 수 있는 방법을 제공
- 문서의 구조·스타일·내용을 변경할 수 있게 함
- **DOM API**: 다른 프로그래밍 언어가 웹 페이지에 접근/조작하도록 페이지 요소를 객체 형태로 제공하며 이에 따른 메서드 또한 제공

### DOM Tree
- 브라우저는 HTML 문서를 해석해 **DOM tree라는 객체 트리**로 구조화
- 객체 간 **상속 구조** 존재
- 문서의 요소(element), 텍스트, 속성이 각각 노드가 됨

### `document` 객체
- **웹 페이지를 나타내는 객체**이자 **DOM Tree의 진입점**
- 예: `document.title` 조회/변경

### DOM 조작 시 기억할 두 단계
1. 조작하고자 하는 요소를 **선택**(또는 탐색)
2. 선택된 요소의 콘텐츠 또는 속성을 **조작**

---

## 9. DOM 선택

### 선택 메서드
```javascript
document.querySelector(selector)     // 요소 한 개 선택
document.querySelectorAll(selector)  // 요소 여러 개 선택
```
- `querySelector()`: 제공한 **CSS selector**를 만족하는 **첫 번째** element 객체 반환 (없으면 `null`)
- `querySelectorAll()`: 만족하는 모든 요소를 **NodeList**로 반환

```javascript
console.log(document.querySelector('.title'))       // 첫 번째 .title 요소
console.log(document.querySelectorAll('.content'))  // NodeList(3)
console.log(document.querySelectorAll('ul > li'))   // NodeList(2)
```

> ✚ **보충**: 구형 메서드 `getElementById()`, `getElementsByClassName()`도 있지만, CSS 선택자를 그대로 쓸 수 있는 `querySelector` 계열이 사실상 표준. 단, `getElementById`가 성능은 미세하게 더 빠름.

---

## 10. DOM 조작

### ① 속성(attribute) 조작

**1. 클래스 속성 조작 — `classList`**
- `element.classList`: 클래스 목록을 **DOMTokenList**(유사 배열) 형태로 반환

| 메서드 | 동작 |
|---|---|
| `classList.add('red')` | 클래스 추가 |
| `classList.remove('red')` | 클래스 제거 |
| `classList.toggle('red')` | 있으면 제거(false 반환), 없으면 추가(true 반환) |

**2. 일반 속성 조작**
| 메서드 | 동작 |
|---|---|
| `getAttribute(name)` | 속성 값 조회 |
| `setAttribute(name, value)` | 속성 값 설정 (이미 있으면 갱신, 없으면 새로 추가) |
| `removeAttribute(name)` | 속성 제거 |

```javascript
const aTag = document.querySelector('a')
console.log(aTag.getAttribute('href'))
aTag.setAttribute('href', 'https://www.naver.com/')
aTag.removeAttribute('href')
```

### ② HTML 콘텐츠 조작 — `textContent`
- 요소의 텍스트 콘텐츠를 표현

```javascript
const h1Tag = document.querySelector('.heading')
console.log(h1Tag.textContent)   // 'DOM 조작'
h1Tag.textContent = '내용 수정'
```

> ✚ **보충 — `textContent` vs `innerHTML`**: `innerHTML`은 HTML 태그를 해석해서 렌더링하기 때문에 사용자 입력을 넣으면 **XSS 공격**에 노출될 수 있음. 텍스트만 다룰 땐 항상 `textContent`를 쓰는 게 안전. (동네레이더 챗봇 카드 렌더링에서도 동일하게 적용되는 원칙)

### ③ DOM 요소 조작
| 메서드 | 동작 |
|---|---|
| `document.createElement(tagName)` | 태그 이름으로 HTML 요소 생성 후 반환 |
| `Node.appendChild(node)` | 부모의 자식 NodeList 마지막에 삽입, 추가된 Node 반환 |
| `Node.removeChild(node)` | 자식 Node 제거, 제거된 Node 반환 |

```javascript
const h1Tag = document.createElement('h1')
h1Tag.textContent = '제목'

const divTag = document.querySelector('div')
divTag.appendChild(h1Tag)
divTag.removeChild(h1Tag)
```

### ④ style 조작
```javascript
const pTag = document.querySelector('p')
pTag.style.color = 'crimson'
pTag.style.fontSize = '2rem'       // CSS의 font-size → camelCase
pTag.style.border = '1px solid black'
```

### (참고) Node vs Element
- **Node**: DOM의 기본 구성 단위. DOM 트리의 각 부분은 Node 객체로 표현
  - Document Node(문서 전체), Element Node(HTML 요소), Text Node(텍스트), Attribute Node(속성)
- **Element**: HTML 요소를 나타내는 **특별한 유형의 Node** (`<p>`, `<div>` 등)
  - Node의 속성/메서드 + 요소 특화 기능(`className`, `innerHTML`, `id` 등)
- **모든 Element는 Node지만, 모든 Node가 Element인 것은 아님**

### (참고) NodeList 주의점
- `querySelectorAll()`이 반환하는 NodeList는 **정적(static)** — DOM이 나중에 변경되어도 이미 선택한 NodeList 값은 변하지 않음

### (참고) DOM 속성 확인 Tip
- 개발자도구 → Elements → **Properties** 탭에서 해당 요소의 모든 DOM 속성 확인 가능

### (참고) 파싱(Parsing)
- 브라우저가 문자열(HTML)을 해석하여 DOM Tree를 만드는 과정 (DOM → Style → Layout → Paint)

---

## 11. Event

### 개념
- **event**: 무언가 일어났다는 신호. **모든 DOM 요소는 event를 만들어 냄**
- **event object**: DOM에서 이벤트가 발생했을 때 생성되는 객체
- 이벤트 종류: mouse, input, keyboard, touch … ([MDN Event 문서](https://developer.mozilla.org/en-US/docs/Web/API/Event) 참고)
- **event handler**(이벤트 처리기): DOM 요소가 받은 event를 '처리'하는 것

### `addEventListener()`
```javascript
EventTarget.addEventListener(type, handler)
// "대상(EventTarget)에 특정 Event(type)가 발생하면, 지정한 이벤트를 받아 할 일(handler)을 등록한다"
```
- **type**: 수신할 이벤트 이름, 문자열로 작성 (예: `'click'`)
- **handler**: 이벤트 발생 시 호출할 콜백 함수. **유일한 매개변수로 event 객체를 자동으로 받음**, 반환값 없음

```javascript
const btn = document.querySelector('#btn')

const detectClick = function (event) {
  console.log(event)                // PointerEvent {...}
  console.log(event.currentTarget)
  event.currentTarget.textContent = "SSAFY"  // <button id="btn">
  console.log(this)                 // <button id="btn"> (currentTarget과 동일)
}

btn.addEventListener('click', detectClick)
```
- 요소에 addEventListener를 부착하면 내부 `this`는 **대상 요소**를 가리킴 (= `event.currentTarget`)

### 버블링 (Bubbling)
- 한 요소에 이벤트가 발생하면 그 요소의 핸들러가 동작하고, 이어서 **부모 요소의 핸들러가 동작**
- 최상단 요소(`document`)를 만날 때까지 이 과정이 반복
- 예: `form > div > p` 구조에서 `p`를 클릭하면 **p → div → form** 순서로 3개의 핸들러가 모두 동작

### `currentTarget` vs `target`
| 속성 | 의미 |
|---|---|
| `event.currentTarget` | **핸들러가 연결된** 요소만 참조 (= `this`) |
| `event.target` | **실제 이벤트가 발생한** 요소를 참조 |

```javascript
// outerouter에만 핸들러 부착 → inner를 클릭해도
// currentTarget: outerouter / target: inner
```

### 버블링의 활용 (이벤트 위임)
- 하위 요소가 여러 개(예: 버튼 100개)일 때, 각각에 핸들러를 부착하는 대신 **공통 조상에 하나만 부착**
- 핸들러에서 `event.target`으로 실제 어느 요소에서 발생했는지 알 수 있기 때문

```javascript
const divTag = document.querySelector('div')
divTag.addEventListener('click', function (event) {
  console.log(event.target)  // 실제 클릭된 button
})
```
> ✚ **보충**: 이 패턴을 **이벤트 위임(Event Delegation)** 이라고 부름. 동적으로 추가되는 요소에도 자동 적용된다는 게 큰 장점 — 리스트가 나중에 늘어나도 핸들러를 다시 붙일 필요 없음.

### event handler 활용 실습 패턴

**1. 클릭 카운터**
```javascript
let counterNumber = 0
const btn = document.querySelector('#btn')

const clickHandler = function () {
  counterNumber += 1
  const spanTag = document.querySelector('#counter')
  spanTag.textContent = counterNumber
}
btn.addEventListener('click', clickHandler)
```

**2. input 실시간 반영**
```javascript
const inputTag = document.querySelector('#text-input')
const pTag = document.querySelector('p')

const inputHandler = function (event) {
  pTag.textContent = event.currentTarget.value
}
inputTag.addEventListener('input', inputHandler)
```

**3. click + input 조합 (클래스 토글)**
```javascript
btn.addEventListener('click', function () {
  pTag.classList.toggle('blue')
})
```

### (주의) console.log(event)에서 currentTarget이 null인 이유
- `currentTarget`은 **이벤트가 처리되는 동안에만** 사용 가능
- 콘솔에 찍힌 객체를 나중에 펼쳐보면 이미 이벤트 처리가 끝나 `null`
- 값 확인이 필요하면 `console.log(event.currentTarget)`처럼 **직접** 출력하거나, 이후 속성은 `event.target` 참고

### 이벤트 기본 동작 취소 — `.preventDefault()`
- 해당 이벤트에 대한 **브라우저 기본 동작을 실행하지 않도록** 지정

```javascript
// 1. 복사 방지
h1Tag.addEventListener('copy', function (event) {
  event.preventDefault()
  alert('복사 할 수 없습니다.')
})

// 2. form 제출 시 페이지 새로고침 취소
const formTag = document.querySelector('#my-form')
const handleSubmit = function (event) {
  event.preventDefault()  // submit의 기본 동작(action 값으로 요청) 취소
}
formTag.addEventListener('submit', handleSubmit)
```
> ✚ **보충**: `preventDefault`는 SPA에서 form을 JS로 처리(fetch/axios 요청)할 때 사실상 필수 첫 줄. 동네레이더 제보 폼 같은 구조에서 이미 쓰고 있는 패턴.

### (주의) addEventListener에서의 화살표 함수와 `this`
```javascript
functionButton.addEventListener('click', function () {
  console.log(this)  // 대상 요소 (button)
})

arrowButton.addEventListener('click', () => {
  console.log(this)  // 화살표 함수는 자신의 this가 없어 상위 스코프의 this (window)
})
```
- **핸들러 안에서 `this`로 요소를 참조하려면 function 키워드 함수 사용**
- 화살표 함수를 쓸 거면 `this` 대신 `event.currentTarget` 사용

---

## ✚ 추가 정리 (강의 외 보충)

### 1. 캡처링(Capturing)도 존재한다
- 이벤트 전파는 사실 **캡처링(위→아래) → 타깃 → 버블링(아래→위)** 3단계
- `addEventListener(type, handler, true)` 세 번째 인자로 캡처링 단계 감지 가능 (실무에선 거의 버블링만 사용)

### 2. 이벤트 제거 — `removeEventListener()`
```javascript
btn.removeEventListener('click', clickHandler)
```
- 등록할 때와 **같은 함수 참조**를 넘겨야 제거됨 → 익명 함수로 등록하면 제거 불가. 핸들러를 변수에 담는 습관이 여기서도 유효.

### 3. `stopPropagation()` vs `preventDefault()`
| | 역할 |
|---|---|
| `event.preventDefault()` | 브라우저 **기본 동작** 취소 (링크 이동, form 제출 등) |
| `event.stopPropagation()` | **버블링(전파) 중단** — 부모 핸들러가 실행되지 않음 |
- 서로 다른 기능이며 필요하면 둘 다 호출

### 4. `DOMContentLoaded`
- `<head>`에서 스크립트를 로드하면 DOM이 만들어지기 전이라 `querySelector`가 `null` 반환
- 해결: `<body>` 끝에 script 배치(강의 방식), 또는:
```javascript
document.addEventListener('DOMContentLoaded', function () { /* ... */ })
// 혹은 <script defer src="...">
```

### 5. NodeList 순회
- `querySelectorAll` 결과는 `forEach`와 `for...of` 사용 가능 (진짜 배열은 아니라서 `map` 등은 `[...nodeList]`로 변환 후 사용)

### 6. 시험/면접 단골 포인트 요약
- `==` vs `===`, falsy 값 목록, `var` 호이스팅 vs `let` TDZ
- `for...in`(객체 key) vs `for...of`(iterable 값)
- 원시 vs 참조 타입의 복사 방식 차이
- `target` vs `currentTarget`, 화살표 함수의 `this`
- 정적 NodeList (실시간 반영 X)