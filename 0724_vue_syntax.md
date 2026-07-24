# Vue — Basic Syntax 정리

> 원본: `0724_데이터트랙_Vue_BasicSyntax.pdf` (SSAFY, 총 123p)
> Vue 3 Composition API / `<script setup>` 기준

## 목차

| # | 챕터 | 핵심 키워드 | 페이지 |
|---|------|------------|--------|
| 1 | Template Syntax | `{{ }}`, `v-html`, Directive 문법 | p.4~19 |
| 2 | Dynamically Data Binding | `v-bind`, 단축어 `:`, Class/Style 바인딩 | p.21~42 |
| 3 | Event Handling | `v-on`, 단축어 `@`, Modifiers | p.44~59 |
| 4 | Form Input Bindings | `v-model`, IME 이슈 | p.61~80 |
| 5 | Conditional Rendering | `v-if`, `v-show` | p.82~93 |
| 6 | List Rendering | `v-for`, `key` | p.95~122 |

---

## 1. Template Syntax (p.4~19)

> **정의**: DOM을 기본 구성 요소 인스턴스의 데이터에 **선언적으로 바인딩**(Vue Instance와 DOM을 연결)할 수 있는 **HTML 기반 템플릿 구문**(확장된 문법 제공)을 사용

### 1-1. Template Syntax 종류 (4가지)

#### ① Text Interpolation

```html
<p>Message: {{ msg }}</p>
```

- 데이터 바인딩의 가장 기본적인 형태
- 이중 중괄호 구문(**콧수염 구문**) 사용
- 콧수염 구문은 해당 구성 요소 인스턴스의 `msg` 속성 값으로 대체됨
- `msg` 속성이 변경될 때마다 업데이트됨

#### ② Raw HTML

```html
<div v-html="rawHtml"></div>
```

```js
const rawHtml = ref('<span style="color:red">This should be red.</span>')
```

- 콧수염 구문은 데이터를 **일반 텍스트로 해석**하기 때문에, 실제 HTML을 출력하려면 `v-html`을 사용해야 함
- vue가 제공하는 특별한 속성 -> 이 경우, 화면에 렌더링 값이 어떤 역할을 하는지 '계산'해야만 한다. 
- v-html을 절대 사용해서는 안되는 상황이 있다! -> 사용자에게 인풋을 받아서 값이 변할 수 있을때
- html에 기본적으로 제공되는 각종 속성들에 내가 가진 state를 반영하고자 한다면? 그냥 class = "msg" 이렇게 작성하면 진짜 'msg' 문자열이 크래스로 등록되어버림. 근데, 내가 바란건 msg라는 변수에 'hello'라는 문자열이 클래스로 등록되기를 바람. 
  이걸 통해서 얻을 수 있는 기대 효과는 msg 변수에 할당된 값이 바뀌면 연결된 class의 이름도 바뀌길 기대한다. 

#### ③ Attribute Bindings

```html
<div v-bind:id="dynamicId"></div>
```

```js
const dynamicId = ref('my-id')
```

렌더링 결과 → `<div id="my-id"></div>`

- 콧수염 구문은 **HTML 속성 내에서 사용할 수 없기 때문에** `v-bind` 사용
- HTML의 `id` 속성 값을 Vue의 `dynamicId` 속성과 동기화되도록 함
- 바인딩 값이 `null`이나 `undefined`인 경우, 렌더링 요소에서 속성이 제거됨

#### ④ JavaScript Expressions

```html
{{ number + 1 }}
{{ ok ? 'YES' : 'NO' }}
{{ message.split('').reverse().join('') }}
<div :id="`list-${id}`"></div>
```

- Vue는 모든 데이터 바인딩 내에서 JavaScript **표현식**의 모든 기능을 지원
- 표현식 사용 가능 위치
  1. 콧수염 구문 내부
  2. 모든 directive의 속성 값 (`v-`로 시작하는 특수 속성)

#### ⚠️ Expressions 주의사항

- 각 바인딩에는 **하나의 단일 표현식**만 포함될 수 있음
  - 표현식 = 값으로 평가할 수 있는 코드 조각 (`return` 뒤에 사용할 수 있는 코드여야 함)
- 작동하지 않는 예:

```html
<!-- 표현식이 아닌 선언식 -->
{{ const number = 1 }}

<!-- 제어문은 사용 불가. 삼항 표현식을 사용해야 함 -->
{{ if (ok) { return message } }}
```

### 1-2. Directive

> **정의**: `v-` 접두사가 있는 특수 속성

**특징**

- Directive의 속성 값은 **단일 JavaScript 표현식**이어야 함 (`v-for`, `v-on` 제외)
- 표현식 값이 변경될 때 **DOM에 반응적으로 업데이트**를 적용

```html
<p v-if="seen">Hi There</p>
```

**전체 구문**

```text
v-on : submit . prevent = "onSubmit"
─┬──   ──┬───   ──┬────    ───┬────
Name  Argument  Modifiers   Value
```

| 구성 | 설명 |
|------|------|
| **Name** | `v-`로 시작. 단축어 사용 시 생략 가능 |
| **Argument** | 콜론(`:`) 또는 단축 기호 뒤에 작성 |
| **Modifiers** | 앞에 점(`.`)을 붙여 표시 |
| **Value** | JavaScript 표현식으로 해석 |

**Arguments** — 일부 directive는 콜론(`:`)으로 표시되는 인자를 사용할 수 있음

```html
<!-- href: <a> 요소의 href 속성 값을 myUrl 값에 바인딩하도록 하는 v-bind의 인자 -->
<a v-bind:href="myUrl">Link</a>

<!-- click: 수신할 이벤트 이름을 작성하는 v-on의 인자 -->
<button v-on:click="doSomething">Button</button>
```

**Modifiers** — 점(`.`)으로 표시되는 특수 접미사. directive가 특별한 방식으로 바인딩되어야 함을 나타냄

```html
<!-- .prevent: 발생한 이벤트에서 event.preventDefault()를 호출하도록 v-on에 지시 -->
<form @submit.prevent="onSubmit">...</form>
```

**Built-in Directives**: `v-text`, `v-show`, `v-if`, `v-for`, …
→ <https://vuejs.org/api/built-in-directives.html>

---

## 2. Dynamically Data Binding — v-bind (p.21~42)

> **정의**: 하나 이상의 속성 또는 컴포넌트 데이터를 표현식에 동적으로 바인딩

**v-bind 사용처**: ① Attribute Bindings ② Class and Style Bindings

### 2-1. Attribute Bindings

- HTML의 속성 값을 Vue의 상태 속성 값과 **동기화**되도록 함

```html
<img v-bind:src="imageSrc">
<a v-bind:href="myUrl">Move to url</a>
```

- **단축어(shorthand)**: `:` (colon)

```html
<img :src="imageSrc">
<a :href="myUrl">Move to url</a>
```

**Dynamic attribute name (동적 인자 이름)**

- 대괄호(`[]`)로 감싸서 directive argument에 JavaScript 표현식을 사용할 수 있음
- 표현식에 따라 동적으로 평가된 값이 최종 argument 값으로 사용됨

```html
<button :[key]="myValue"></button>
```

> ⚠️ 대괄호 안에 작성하는 이름은 **반드시 소문자로만** 구성 가능 (브라우저가 속성 이름을 소문자로 강제 변환하기 때문)

**전체 예시 (VBind.vue)**

```vue
<template>
  <div>
    <img :src="imageSrc">
    <a :href="myUrl">Move to url</a>
    <p :[dynamicattr]="dynamicValue">Dynamic Attr</p>
  </div>
</template>

<script setup>
  import { ref } from 'vue'

  const imageSrc = ref('https://picsum.photos/200')
  const myUrl = ref('https://www.google.co.kr/')
  const dynamicattr = ref('title')
  const dynamicValue = ref('Hello Vue.js')
</script>
```

렌더링 결과 → `<p title="Hello Vue.js">Dynamic Attr</p>`

### 2-2. Class and Style Bindings

- `class`와 `style`은 모두 HTML 속성이므로, 다른 속성과 마찬가지로 `v-bind`로 동적으로 문자열 값을 할당할 수 있음
- Vue는 `class`/`style` 속성 값을 `v-bind`로 사용할 때 **객체 또는 배열**을 활용해 작성할 수 있도록 함
  - 단순 문자열 연결로 값을 생성하는 것은 번거롭고 오류가 발생하기 쉽기 때문

가능한 경우 4가지:

1. Binding HTML Classes — 1.1 객체 / 1.2 배열
2. Binding Inline Styles — 2.1 객체 / 2.2 배열

#### 1.1 클래스 — 객체 바인딩

객체를 `:class`에 전달하여 클래스를 동적으로 전환

```js
const isActive = ref(true)
```

```html
<div :class="{ active: isActive }">Text</div>
<!-- → <div class="active">Text</div> -->
```

객체에 여러 필드를 포함해 다중 클래스 전환 가능. 일반 `class` 속성과 함께 사용 가능

```js
const isActive = ref(false)
const hasInfo = ref(true)
```

```html
<div class="static" :class="{ active: isActive, 'text-primary': hasInfo }">Text</div>
<!-- → <div class="static text-primary">Text</div> -->
```

inline 방식 대신 반응형 변수로 객체를 한번에 작성하는 방법

```js
// ref는 반응 객체의 속성으로 액세스되거나 변경될 때 자동으로 unwrap
const classObj = ref({
  active: isActive,
  'text-primary': hasInfo
})
```

```html
<div class="static" :class="classObj">Text</div>
```

#### 1.2 클래스 — 배열 바인딩

`:class`를 배열에 바인딩하여 클래스 목록 적용

```js
const activeClass = ref('active')
const infoClass = ref('text-primary')
```

```html
<div :class="[activeClass, infoClass]">Text</div>
<!-- → <div class="active text-primary">Text</div> -->
```

배열 구문 내에서 객체 구문 사용 가능

```html
<div :class="[{ active: isActive }, infoClass]">Text</div>
<!-- isActive가 false면 → <div class="text-primary">Text</div> -->
```

#### 2.1 스타일 — 객체 바인딩

`:style`은 JavaScript 객체 값에 대한 바인딩을 지원 (HTML `style` 속성에 해당)

```js
const activeColor = ref('crimson')
const fontSize = ref(50)
```

```html
<div :style="{ color: activeColor, fontSize: fontSize + 'px' }">Text</div>
<!-- → <div style="color: crimson; font-size: 50px;">Text</div> -->
```

- 실제 CSS처럼 **kebab-cased 키 문자열도 지원** (단, **camelCase 작성을 권장**)

```html
<div :style="{ color: activeColor, 'font-size': fontSize + 'px' }">Text</div>
```

- 반응형 변수로 스타일 객체를 한번에 작성 가능

```js
const styleObj = ref({
  color: activeColor,
  fontSize: fontSize.value + 'px'
})
```

```html
<div :style="styleObj">Text</div>
```

#### 2.2 스타일 — 배열 바인딩

- 여러 스타일 객체를 배열에 작성해서 `:style`에 바인딩 가능
- 작성한 객체는 **병합되어 동일한 요소에 적용**

```js
const styleObj2 = ref({
  color: 'blue',
  border: '1px solid black'
})
```

```html
<div :style="[styleObj, styleObj2]">Text</div>
<!-- → <div style="color: blue; font-size: 50px; border: 1px solid black;"> -->
```

📚 v-bind 종합: <https://vuejs.org/api/built-in-directives.html#v-bind>

---

## 3. Event Handling — v-on (p.44~59)

> **정의**: DOM 요소에 이벤트 리스너를 연결 및 수신

**구성**

```text
v-on:event="handler"
```

- handler 종류
  1. **Inline handlers**: 이벤트가 트리거될 때 실행될 JavaScript 코드
  2. **Method handlers**: 컴포넌트에 정의된 메서드 이름
- **단축어(shorthand)**: `@` → `@event="handler"`

### 3-1. Inline Handlers

주로 간단한 상황에 사용

```js
const count = ref(0)
```

```html
<button @click="count++">Add 1</button>
<p>Count: {{ count }}</p>
```

### 3-2. Method Handlers

Inline handlers로는 불가능한 대부분의 상황에서 사용

```js
const name = ref('Alice')

const myFunc = function (event) {
  console.log(event)                 // PointerEvent {isTrusted: true, …}
  console.log(event.currentTarget)   // <button>Hello</button>
  console.log(`Hello ${name.value}!`)  // Hello Alice!
}
```

```html
<button @click="myFunc">Hello</button>
```

- Method Handlers는 이를 트리거하는 **기본 DOM Event 객체를 자동으로 수신**

### 3-3. 사용자 지정 인자 전달

기본 이벤트 대신 사용자 지정 인자를 전달할 수도 있음

```js
const greeting = function (message) {
  console.log(message)
}
```

```html
<button @click="greeting('hello')">Say hello</button>
<button @click="greeting('bye')">Say bye</button>
```

### 3-4. Inline Handlers에서의 event 인자 접근

- Inline Handlers에서 원래 DOM 이벤트에 접근하려면 **`$event` 변수**를 사용해 메서드에 전달

```js
const warning = function (message, event) {
  console.log(message)  // 경고입니다.
  console.log(event)    // PointerEvent {…}
}
```

```html
<button @click="warning('경고입니다.', $event)">Warning</button>
```

- `$event` 변수를 전달하는 **위치는 상관 없음**

```js
const danger = function (msg1, event, msg2) {
  console.log(msg1)   // 위험
  console.log(event)  // PointerEvent {…}
  console.log(msg2)   // 합니다
}
```

```html
<button @click="danger('위험', $event, '합니다')">Danger</button>
```

### 3-5. Modifiers

**Event Modifiers**

- Vue는 `v-on`에 대한 Event Modifiers를 제공해 `event.preventDefault()` 같은 구문을 메서드에서 직접 작성하지 않도록 함
- `stop`, `prevent`, `self` 등 다양한 modifiers 제공
- ➤ 메서드는 DOM 이벤트 처리보다는 **데이터에 관한 논리 작성에 집중**할 것

```html
<form @submit.prevent="onSubmit">...</form>
<a @click.stop.prevent="onLink">...</a>
```

> ⚠️ Modifiers는 **체이닝(chained)** 가능하며, 이때 **작성된 순서로 실행**되므로 작성 순서에 유의

**Key Modifiers**

- 키보드 이벤트 수신 시 특정 키에 관한 별도 modifiers 사용 가능

```html
<!-- key가 Enter일 때만 onSubmit 호출 -->
<input @keyup.enter="onSubmit">
```

📚 v-on 종합: <https://vuejs.org/api/built-in-directives.html#v-on>

---

## 4. Form Input Bindings — v-model (p.61~80)

**개요**: form 처리 시 사용자가 input에 입력하는 값을 실시간으로 JavaScript 상태에 동기화해야 하는 경우 → **양방향 바인딩**

양방향 바인딩 방법 2가지:

1. `v-bind`와 `v-on`을 함께 사용
2. `v-model` 사용

### 4-1. v-bind와 v-on을 함께 사용

1. `v-bind`로 input 요소의 `value` 속성 값을 입력 값으로 사용
2. `v-on`으로 `input` 이벤트가 발생할 때마다 input 요소의 `value` 값을 별도 반응형 변수에 저장하는 핸들러를 호출

```js
const inputText1 = ref('')

const onInput = function (event) {
  inputText1.value = event.currentTarget.value
}
```

```html
<p>{{ inputText1 }}</p>
<input :value="inputText1" @input="onInput">
```

### 4-2. v-model 사용

> **정의**: form input 요소 또는 컴포넌트에서 양방향 바인딩을 만듦

사용자 입력 데이터와 반응형 변수를 실시간 동기화

```js
const inputText2 = ref('')
```

```html
<p>{{ inputText2 }}</p>
<input v-model="inputText2">
```

> ⚠️ **IME가 필요한 언어(한국어, 중국어, 일본어 등)의 경우 v-model이 제대로 업데이트되지 않음**
> → 해당 언어에 올바르게 응답하려면 **v-bind와 v-on 방법을 사용**해야 함

### 4-3. v-model 활용 (다양한 입력 양식)

`v-model`은 단순 Text input뿐만 아니라 **Checkbox, Radio, Select** 등 다양한 타입의 사용자 입력 방식과 함께 사용 가능

**① 단일 체크박스 + boolean 값**

```js
const checked = ref(false)
```

```html
<input type="checkbox" id="checkbox" v-model="checked">
<label for="checkbox">{{ checked }}</label>
<!-- 체크: true / 해제: false -->
```

**② 여러 체크박스 + 배열** — 배열에는 현재 선택된 체크박스의 값이 포함됨

```js
const checkedNames = ref([])
```

```html
<div>Checked names: {{ checkedNames }}</div>

<input type="checkbox" id="alice" value="Alice" v-model="checkedNames">
<label for="alice">Alice</label>

<input type="checkbox" id="bella" value="Bella" v-model="checkedNames">
<label for="bella">Bella</label>
<!-- 둘 다 체크 시 → Checked names: [ "Alice", "Bella" ] -->
```

**③ Select**

- `v-model` 표현식의 초기 값이 어떤 option과도 일치하지 않으면, select 요소는 "선택되지 않은(unselected)" 상태로 렌더링됨

```js
const selected = ref('')
```

```html
<div>Selected: {{ selected }}</div>

<select v-model="selected">
  <option disabled value="">Please select one</option>
  <option>Alice</option>
  <option>Bella</option>
  <option>Cathy</option>
</select>
```

📚 v-model 종합: <https://vuejs.org/api/built-in-directives.html#v-model>

### 📌 [참고] '$' 접두어가 붙은 변수

- Vue 인스턴스 내에서 제공되는 **내부 변수**
- 사용자가 지정한 반응형 변수나 메서드와 **구분하기 위함**
- 주로 Vue 인스턴스 내부 상태를 다룰 때 사용 (예: `$event`)

### 📌 [참고] IME (Input Method Editor)

- 사용자가 입력 장치에서 기본적으로 사용할 수 없는 문자(비영어권 언어)를 입력할 수 있도록 하는 **운영 체제 구성 프로그램**
- 일반적으로 키보드 키보다 자모가 더 많은 언어에서 사용
- ➤ IME가 동작하는 방식과 Vue의 양방향 바인딩(`v-model`) 동작 방식이 **상충**하기 때문에, 한국어 입력 시 예상대로 동작하지 않았던 것

---

## 5. Conditional Rendering (p.82~93)

### 5-1. v-if

> **정의**: 표현식 값의 `true`/`false`를 기반으로 요소를 **조건부로 렌더링**

**v-else** — `v-if`에 대한 else 블록

```js
const isSeen = ref(true)
```

```html
<p v-if="isSeen">true일때 보여요</p>
<p v-else>false일때 보여요</p>
<button @click="isSeen = !isSeen">토글</button>
```

**v-else-if** — `v-if`에 대한 else if 블록

```js
const name = ref('Cathy')
```

```html
<div v-if="name === 'Alice'">Alice입니다</div>
<div v-else-if="name === 'Bella'">Bella입니다</div>
<div v-else-if="name === 'Cathy'">Cathy입니다</div>
<div v-else>아무도 아닙니다.</div>
```

**여러 요소에 대한 v-if 적용**
> 영역을 만드는게 template 태그

- HTML `<template>` 요소에 `v-if`를 사용해 하나 이상의 요소에 적용 가능 (`v-else`, `v-else-if` 모두 적용 가능)

```html
<template v-if="name === 'Cathy'">
  <div>Cathy입니다</div>
  <div>나이는 30살입니다</div>
</template>
<!-- 렌더링 결과에 template 태그는 포함되지 않음 -->
```

### 📌 [참고] HTML `<template>` element

- 페이지가 로드될 때 렌더링되지 않지만, JavaScript를 사용해 나중에 문서에서 사용할 수 있도록 하는 HTML을 보유하기 위한 메커니즘
- ➤ **"보이지 않는 wrapper 역할"**

### 5-2. v-show

> **정의**: 표현식 값의 `true`/`false`를 기반으로 요소의 **가시성(visibility)을 전환**

- `v-show` 요소는 **항상 DOM에 렌더링되어 있음** — CSS `display` 속성만 전환하기 때문

```js
const isShow = ref(false)
```

```html
<div v-show="isShow">v-show</div>
<!-- → <div style="display: none;">v-show</div> -->
```

### 5-3. v-if vs. v-show — 적절한 사용처

| | **v-if** | **v-show** |
|---|---|---|
| 특성 | Cheap initial load, expensive toggle | Expensive initial load, cheap toggle |
| 동작 | 초기 조건이 false면 아무 작업도 수행하지 않음 | 초기 조건에 관계없이 항상 렌더링 |
| 비용 | 토글 비용이 높음 | 초기 렌더링 비용이 더 높음 |

> ➤ 콘텐츠를 **매우 자주 전환**해야 하면 `v-show`, **실행 중에 조건이 변경되지 않으면** `v-if` 권장

---

## 6. List Rendering — v-for (p.95~122)

> **정의**: 소스 데이터를 기반으로 요소 또는 템플릿 블록을 여러 번 렌더링
> (Array, Object, Number, String, Iterable)

### 6-1. v-for 구조

- `v-for`는 **`alias in expression`** 형식의 특수 구문 사용

```html
<div v-for="item in items">
  {{ item.text }}
</div>
```

- 인덱스(객체에서는 key)에 대한 별칭 지정 가능

```html
<div v-for="(item, index) in arr"></div>

<div v-for="value in object"></div>
<div v-for="(value, key) in object"></div>
<div v-for="(value, key, index) in object"></div>
```

### 6-2. v-for 예시

**배열 반복**

```js
const myArr = ref([
  { name: 'Alice', age: 20 },
  { name: 'Bella', age: 21 }
])
```

```html
<div v-for="(item, index) in myArr">
  {{ index }} / {{ item.name }}
</div>
<!-- 0 / Alice, 1 / Bella -->
```

**객체 반복**

```js
const myObj = ref({
  name: 'Cathy',
  age: 30
})
```

```html
<div v-for="(value, key, index) in myObj">
  {{ index }} / {{ key }} / {{ value }}
</div>
<!-- 0 / name / Cathy, 1 / age / 30 -->
```

**여러 요소에 대한 v-for 적용** — `<template>`에 v-for 사용

```html
<ul>
  <template v-for="item in myArr">
    <li>{{ item.name }}</li>
    <li>{{ item.age }}</li>
    <hr>
  </template>
</ul>
```

**중첩된 v-for** — 각 v-for 범위는 상위 범위에 접근 가능

```js
const myInfo = ref([
  { name: 'Alice', age: 20, friends: ['Bella', 'Cathy', 'Dan'] },
  { name: 'Bella', age: 21, friends: ['Alice', 'Cathy'] }
])
```

```html
<ul v-for="item in myInfo">
  <li v-for="friend in item.friends">
    {{ item.name }} - {{ friend }}
  </li>
</ul>
```

### 6-3. v-for with key ★

> **반드시 v-for와 key를 함께 사용한다**
> — 내부 컴포넌트의 상태를 일관되게 하여 데이터의 예측 가능한 행동을 유지하기 위함

- `key`는 반드시 **각 요소에 대한 고유한 값을 나타낼 수 있는 식별자**여야 함

```js
let id = 0

const items = ref([
  { id: id++, name: 'Alice' },
  { id: id++, name: 'Bella' },
])
```

```html
<div v-for="item in items" :key="item.id">
  <!-- content -->
</div>
```

**내장 특수 속성 key**

- `number` 혹은 `string`으로만 사용해야 함
- Vue의 내부 **가상 DOM 알고리즘**이 이전 목록과 새 노드 목록을 비교할 때 **각 node를 식별하는 용도**로 사용
- ➤ Vue 내부 동작과 관련된 부분이므로 최대한 작성할 것
- 📚 <https://vuejs.org/api/built-in-special-attributes.html#key>

**올바른 key 선택 기준**

| 권장되는 key 값 | 피해야 할 key 값 |
|---|---|
| 데이터베이스의 고유 ID | 배열 인덱스(index) |
| 항목 고유 식별자 (예: UUID) | 객체 자체 |

### 6-4. v-for with v-if ★

> **동일 요소에 v-for와 v-if를 함께 사용하지 않는다**
> — 동일한 요소에서 **v-if가 v-for보다 우선순위가 더 높기 때문**
> ➤ v-if에서의 조건은 v-for 범위의 변수에 접근할 수 없음

**문제 상황** — todo 데이터 중 이미 처리한(`isComplete === true`) todo만 출력하기

```js
let id = 0

const todos = ref([
  { id: id++, name: '복습', isComplete: true },
  { id: id++, name: '예습', isComplete: false },
  { id: id++, name: '저녁식사', isComplete: true },
  { id: id++, name: '노래방', isComplete: false }
])
```

```html
<ul>
  <li v-for="todo in todos" v-if="!todo.isComplete" :key="todo.id">
    {{ todo.name }}
  </li>
</ul>
```

→ ❌ `Uncaught TypeError: Cannot read properties of undefined (reading 'isComplete')`
(v-if가 먼저 평가되어 `todo`가 아직 정의되지 않은 상태)

> ※ 슬라이드 원문 기준: 목표 문구는 "이미 처리한(true) todo 출력"인데 예시 코드 조건은 `!todo.isComplete`(미완료)로 적혀 있음. 핵심은 우선순위 문제와 아래 해결 패턴이니, 실제 조건은 목표에 맞게 조정해서 쓰면 됨.

**해결법 2가지**

**① computed 활용** — 필터링된 목록을 반환하여 반복하도록 설정

```js
import { ref, computed } from 'vue'

const completeTodos = computed(() => {
  return todos.value.filter((todo) => !todo.isComplete)
})
```

```html
<ul>
  <li v-for="todo in completeTodos" :key="todo.id">
    {{ todo.name }}
  </li>
</ul>
```

**② v-for와 `<template>` 요소 활용** — v-if 위치를 이동

```html
<ul>
  <template v-for="todo in todos" :key="todo.id">
    <li v-if="!todo.isComplete">
      {{ todo.name }}
    </li>
  </template>
</ul>
```

📚 v-for 종합: <https://vuejs.org/api/built-in-directives.html#v-for>

### 📌 [참고] 배열과 v-for

**배열 변경 관련 메서드** — v-for와 배열 함께 사용 시 배열 메서드 주의

| 구분 | 동작 | 메서드 |
|---|---|---|
| **변화 메서드** | 호출하는 **원본 배열을 변경** | `push()`, `pop()`, `shift()`, `unshift()`, `splice()`, `sort()`, `reverse()` |
| **배열 교체** | 원본을 수정하지 않고 **항상 새 배열을 반환** | `filter()`, `concat()`, `slice()` |

**v-for와 배열을 활용해 "필터링/정렬" 활용하기**

원본 데이터를 수정하거나 교체하지 않고, 필터링·정렬된 새로운 데이터를 표시하는 방법:

**① computed 활용** — 원본 기반으로 필터링된 새로운 결과를 생성

```js
const numbers = ref([1, 2, 3, 4, 5])

const evenNumbers = computed(() => {
  return numbers.value.filter((number) => number % 2 === 0)
})
```

```html
<li v-for="num in evenNumbers">{{ num }}</li>
```

**② method 활용** — computed가 불가능한 **중첩된 v-for**의 경우 사용

```js
const numberSets = ref([
  [1, 2, 3, 4, 5],
  [6, 7, 8, 9, 10]
])

const evenNumbers = function (numbers) {
  return numbers.filter((number) => number % 2 === 0)
}
```

```html
<ul v-for="numbers in numberSets">
  <li v-for="num in evenNumbers(numbers)">{{ num }}</li>
</ul>
```

**※주의※ 배열의 인덱스를 v-for의 key로 사용하지 말 것**

```html
<!-- ❌ 이렇게 쓰지 말 것 -->
<div v-for="(item, index) in items" :key="index">
  <!-- content -->
</div>
```

- 인덱스는 식별자가 아닌 **배열의 항목 위치**만 나타내기 때문
- 새 요소가 배열의 끝이 아닌 위치에 삽입되면, 이미 반복된 구성 요소 데이터가 함께 업데이트되지 않기 때문
- ➤ 직접 고유한 값을 만들어내는 메서드를 만들거나, 외부 라이브러리 등을 활용하는 등 **식별자 역할을 할 수 있는 값**을 만들어 사용

---

## 부록 — 한눈 요약

### 디렉티브 치트시트

| 디렉티브 | 단축어 | 역할 |
|---|---|---|
| `v-bind` | `:` | 속성/클래스/스타일 동적 바인딩 |
| `v-on` | `@` | 이벤트 리스너 연결 및 수신 |
| `v-model` | — | form 요소 양방향 바인딩 |
| `v-html` | — | Raw HTML 출력 |
| `v-if` / `v-else-if` / `v-else` | — | 조건부 렌더링 (DOM 생성/제거) |
| `v-show` | — | 가시성 전환 (`display`만 토글) |
| `v-for` | — | 목록 렌더링 (`:key` 필수) |

### 꼭 기억할 규칙

1. 바인딩에는 **단일 표현식**만 — 선언문·제어문 불가, 삼항 표현식은 가능
2. 동적 인자 `[ ]` 안은 **소문자만**
3. `v-model`은 IME 언어(한국어)에서 실시간 반영 안 됨 → `v-bind` + `v-on` 사용
4. `v-for`에는 반드시 `:key` — number/string 타입의 고유 식별자, **인덱스·객체 금지**
5. 동일 요소에 `v-for` + `v-if` 금지 (v-if 우선순위가 높음) → **computed** 또는 **`<template>` 분리**로 해결
6. 자주 토글 → `v-show` / 실행 중 조건 변경 없음 → `v-if`
7. 배열 변화 메서드(`push` 등)는 원본 변경, `filter`/`concat`/`slice`는 새 배열 반환 → 반환값으로 교체 필요
8. Event Modifiers 체이닝은 **작성 순서대로 실행**
9. `<template>` 태그는 보이지 않는 wrapper — v-if/v-for를 여러 요소에 묶어 적용할 때 사용
10. `$` 접두어 = Vue 인스턴스 내부 변수 (예: `$event`)