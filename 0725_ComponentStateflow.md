# Vue.js — Component State Flow

> 출처: `16기_데이터트랙_0727_1_ComponentStateFlow.pdf` (총 112페이지)
> 범위: Passing Props / Component Events / Computed / Watchers / Lifecycle Hooks / Virtual DOM

## 한눈에 보기

- 부모 → 자식으로 데이터를 내리는 **props**와, 자식 → 부모로 신호를 올리는 **emit**의 짝을 이해한다.
- 왜 Vue가 굳이 **단방향**을 강제하는지, 자식이 부모 데이터를 바꾸고 싶을 때 어떻게 해야 하는지 설명할 수 있다.
- **computed / methods / watch** 세 가지를 언제 각각 써야 하는지 구분한다.
- Vue가 실제 DOM을 어떻게 다루는지(**Virtual DOM**)와, 직접 DOM을 만지면 안 되는 이유를 안다.

## 목차

1. [Passing Props](#1-passing-props) (p.4-41)
2. [Component Events](#2-component-events) (p.42-71)
3. [Computed Properties](#3-computed-properties) (p.72-84, 95-97)
4. [Watchers](#4-watchers) (p.85-94)
5. [Lifecycle Hooks](#5-lifecycle-hooks) (p.98-105)
6. [Virtual DOM](#6-virtual-dom) (p.106-111)
7. [정리 체크리스트](#7-정리-체크리스트)
8. [복습 문제](#8-복습-문제)

---

## 1. Passing Props

### 1-1. 왜 props가 필요한가 (p.6-8)

같은 데이터가 한 화면의 여러 위치에서 반복 출력되는 상황을 생각해 보자. 페이지를 구성하는 컴포넌트가 여러 개일 때, 각 컴포넌트가 **개별적으로 동일한 데이터를 관리**하면 값이 하나 바뀔 때마다 모든 컴포넌트에 변경을 요청해야 한다.

> **결론** — "공통된 부모 컴포넌트에서 관리하자"

여기서 컴포넌트 간 통신의 두 방향이 나온다.

```text
부모 --------- props (데이터 전달) --------→ 자식
부모 ←-------- $emit (일어난 일 알림) ------- 자식
```

**Props**: 부모 컴포넌트로부터 자식 컴포넌트로 데이터를 전달하는 데 사용되는 속성.

### 1-2. Props 특징과 One-Way Data Flow (p.9-11)

| 방향 | 가능 여부 |
|---|---|
| 부모 속성 업데이트 → 자식으로 전달 | O |
| 자식이 props를 변경 → 부모로 전달 | X (시도 자체가 불가능) |

- 자식 컴포넌트 내부에서 props를 변경하려고 **시도해서는 안 되며 불가능하다.**
- 부모 컴포넌트가 업데이트될 때마다, 이를 사용하는 자식 컴포넌트의 **모든 props가 최신 값으로 업데이트**된다.
- 즉, 부모 컴포넌트에서만 변경하고 이를 내려받는 자식 컴포넌트는 자연스럽게 갱신된다.

모든 props는 자식 속성과 부모 속성 사이에 **하향식 단방향 바인딩(one-way-down binding)** 을 형성한다.

> **단방향인 이유** — 하위 컴포넌트가 실수로 상위 컴포넌트의 상태를 변경하여 앱에서의 데이터 흐름을 이해하기 어렵게 만드는 것을 방지하기 위함. 핵심 키워드는 데이터 흐름의 **"일관성"** 과 **"단순화"**.

### 1-3. 실습 사전 준비 (p.13-16)

1. vue 프로젝트 생성
2. 초기 생성된 컴포넌트 모두 삭제 (`App.vue` 제외)
3. `src/assets` 내부 파일 모두 삭제
4. `main.js`에서 해당 코드 삭제

```js
// main.js

import './assets/main.css'
```

5. `App > Parent > ParentChild` 컴포넌트 관계 작성

```vue
<!-- App.vue -->

<template>
  <div>
    <Parent />
  </div>
</template>

<script setup>
import Parent from '@/components/Parent.vue'
</script>
```

```vue
<!-- Parent.vue -->

<template>
  <div>
    <ParentChild />
  </div>
</template>

<script setup>
import ParentChild from '@/components/ParentChild.vue'
</script>
```

```vue
<!-- ParentChild.vue -->

<template>
  <div></div>
</template>

<script setup>
</script>
```

### 1-4. Props 작성과 선언 (p.17-22)

부모가 내려보낸 props를 사용하려면 **자식 컴포넌트에서 명시적인 props 선언이 필요**하다.

부모 쪽에서는 속성처럼 작성한다. `my-msg="message"`에서 `my-msg`가 **props 이름**, `"message"`가 **props 값**이다.

```vue
<!-- Parent.vue -->

<template>
  <div>
    <ParentChild my-msg="message" />
  </div>
</template>
```

자식 쪽에서는 `defineProps()`로 선언한다. 인자의 데이터 타입에 따라 선언 방식이 두 가지로 나뉜다.

**1. 문자열 배열을 사용한 선언** — 배열의 문자열 요소 이름이 곧 전달된 props의 이름이다.

```vue
<!-- ParentChild.vue -->

<script setup>
defineProps(['myMsg'])
</script>
```

**2. 객체를 사용한 선언** — 각 객체 속성의 키가 전달받은 props 이름이 되며, 값은 해당 데이터 타입의 생성자 함수(`Number`, `String` 등)여야 한다.

```vue
<!-- ParentChild.vue -->

<script setup>
defineProps({
  myMsg: String
})
</script>
```

> **객체 선언 문법 사용을 권장한다.** 이유는 [2-8절](#2-8-주의-객체-선언-방식을-권장하는-이유-p70)에서 다룬다.

### 1-5. props 데이터 사용 (p.23-24)

선언 후 템플릿에서 **반응형 변수와 같은 방식**으로 활용한다.

```vue
<!-- ParentChild.vue -->

<div>
  <p>{{ myMsg }}</p>
</div>
```

`defineProps()`는 props를 **객체로 반환**하므로, 필요한 경우 JavaScript에서도 접근할 수 있다.

```vue
<script setup>
const props = defineProps({ myMsg: String })
console.log(props)        // {myMsg: 'message'}
console.log(props.myMsg)  // 'message'
</script>
```

### 1-6. 한 단계 더 props 내려 보내기 (p.25-27)

`ParentChild`를 부모로 갖는 `ParentGrandChild`를 만들고, 받은 props를 그대로 다시 내려보낸다.

```vue
<!-- ParentChild.vue -->

<template>
  <div>
    <p>{{ myMsg }}</p>
    <ParentGrandChild :my-msg="myMsg" />
  </div>
</template>

<script setup>
import ParentGrandChild from '@/components/ParentGrandChild.vue'

defineProps({
  myMsg: String,
})
</script>
```

```vue
<!-- ParentGrandChild.vue -->

<template>
  <div>
    <p>{{ myMsg }}</p>
  </div>
</template>

<script setup>
defineProps({
  myMsg: String,
})
</script>
```

여기서 `:my-msg="myMsg"`는 **v-bind를 사용한 동적 props**다.

> `ParentGrandChild`가 출력하는 props는 결국 `Parent`에 정의되어 있는 props다. **`Parent`가 props를 변경하면 이를 전달받는 `ParentChild`, `ParentGrandChild`에서도 모두 업데이트된다.**

### 1-7. Props 세부사항 (p.29-34)

#### Props Name Casing (p.30)

| 위치 | 표기법 | 예시 |
|---|---|---|
| 자식 컴포넌트로 **전달** 시 | kebab-case | `<ParentChild my-msg="message" />` |
| **선언** 및 템플릿 **참조** 시 | camelCase | `defineProps({ myMsg: String })` / `{{ myMsg }}` |

> 전달 시 기술적으로 camelCase도 가능하나, **HTML 속성 표기법과 동일하게 kebab-case로 표기할 것을 권장**한다.

#### Static Props와 Dynamic Props (p.31-34)

지금까지 작성한 것은 모두 Static(정적) props다. **v-bind를 사용하면 동적으로 할당된 props**를 쓸 수 있다.

```vue
<!-- Parent.vue -->

import { ref } from 'vue'

const name = ref('Alice')
```

```vue
<!-- Parent.vue -->

<ParentChild my-msg="message" :dynamic-props="name" />
```

```vue
<!-- ParentChild.vue -->

defineProps({
  myMsg: String,
  dynamicProps: String,
})
```

```vue
<!-- ParentChild.vue -->

<p>{{ dynamicProps }}</p>
```

`name`이 `ref`이므로, 값이 바뀌면 자식에 표시되는 `dynamicProps`도 함께 바뀐다.

### 1-8. Props 활용: v-for와 함께 쓰기 (p.36-39)

반복되는 요소를 props로 전달하는 패턴이다. `ParentItem` 컴포넌트를 만들어 `Parent`의 하위로 등록한 뒤, 배열을 순회하며 각 항목을 내려보낸다.

```js
// Parent.vue

const items = ref([
  { id: 1, name: '사과' },
  { id: 2, name: '바나나' },
  { id: 3, name: '딸기' }
])
```

```vue
<!-- Parent.vue -->

<ParentItem
  v-for="item in items"
  :key="item.id"
  :my-prop="item"
/>
```

객체 전체를 넘겼으므로 자식에서는 `Object` 타입으로 선언하고 속성에 접근한다.

```vue
<!-- ParentItem.vue -->

<template>
  <div>
    <p>{{ myProp.id }}</p>
    <p>{{ myProp.name }}</p>
  </div>
</template>

<script setup>
defineProps({
  myProp: Object
})
</script>
```

> **`:key="item.id"` 를 빼먹지 말 것.** v-for와 컴포넌트를 함께 쓸 때 key는 필수다.

---

## 2. Component Events

### 2-1. $emit (p.43-45)

props는 부모 → 자식 단방향이므로, 자식이 부모의 데이터를 바꾸고 싶다면 **부모에게 "변경해 달라"고 요청**해야 한다. 그 수단이 `$emit`이다.

**$emit()**: 자식 컴포넌트가 이벤트를 발생시켜 부모 컴포넌트로 데이터를 전달하는 역할의 메서드.

> `$` 표기는 Vue 인스턴스의 내부 변수들을 가리킨다. Life cycle hooks, 인스턴스 메서드 등 내부 특정 속성에 접근할 때 사용한다.

```js
$emit(event, ...args)
```

| 인자 | 설명 |
|---|---|
| `event` | 발신할 이벤트 이름 |
| `...args` | 추가 인자 (선택) |

### 2-2. 이벤트 발신 및 수신 (p.47-50)

`$emit`을 사용하여 **템플릿 표현식에서 직접** 사용자 정의 이벤트를 발신할 수 있다.

```vue
<!-- ParentChild.vue -->

<button @click="$emit('someEvent')">클릭</button>
```

부모는 `v-on`을 사용하여 수신한다.

```vue
<!-- Parent.vue -->

<ParentChild @some-event="someCallback" my-msg="message" :dynamic-props="name" />
```

```js
// Parent.vue

const someCallback = function () {
  console.log('ParentChild가 발신한 이벤트를 수신했어요.')
}
```

### 2-3. emit 이벤트 선언 — defineEmits (p.52-53)

`defineEmits()`를 사용하여 발신할 이벤트를 선언한다. props와 마찬가지로 인자의 데이터 타입에 따라 선언 방식이 나뉜다(배열, 객체).

> **왜 필요한가** — `<script>` 안에서는 `$emit` 메서드에 접근할 수 없다. `defineEmits()`는 `$emit` 대신 사용할 수 있는 **동등한 함수를 반환**한다.

```vue
<!-- ParentChild.vue -->

<script setup>
const emit = defineEmits(['someEvent'])

const buttonClick = function () {
  emit('someEvent')
}
</script>
```

```vue
<button @click="buttonClick">클릭</button>
```

### 2-4. 이벤트 인자 전달 (p.55-58)

이벤트 발신 시 추가 인자를 전달하여 값을 제공할 수 있다.

```js
// ParentChild.vue

const emit = defineEmits(['someEvent', 'emitArgs'])

const emitArgs = function () {
  emit('emitArgs', 1, 2, 3)
}
```

```vue
<button @click="emitArgs">추가 인자 전달</button>
```

부모 쪽에서는 나머지 매개변수(`...args`)로 받는다.

```vue
<!-- Parent.vue -->

<ParentChild
  @some-event="someCallback"
  @emit-args="getNumbers"
  my-msg="message"
  :dynamic-props="name"
/>
```

```js
const getNumbers = function (...args) {
  console.log(args)  // (3) [1, 2, 3]
  console.log(`ParentChild가 전달한 추가인자 ${args}를 수신했어요.`)
}
```

### 2-5. Event Name Casing (p.60)

props와 방향이 **같다**. 선언·발신은 camelCase, 부모의 수신은 kebab-case.

| 위치 | 표기법 | 예시 |
|---|---|---|
| **선언 및 발신** 시 | camelCase | `emit('someEvent')` / `defineEmits(['someEvent'])` |
| 부모에서 **수신** 시 | kebab-case | `<ParentChild @some-event="..." />` |

### 2-6. emit 실습 — 손자에서 조부모까지 (p.62-66)

**목표**: 최하단 자식인 `ParentGrandChild`에서 `Parent` 컴포넌트의 `name` 변수 변경을 요청하기.

이벤트는 한 번에 건너뛸 수 없으므로 **한 단계씩 위로 릴레이**한다.

```text
ParentGrandChild --emit--> ParentChild --emit--> Parent (실제 변경)
```

**1단계** — `ParentGrandChild`에서 이름 변경을 요청하는 이벤트 발신

```js
// ParentGrandChild.vue

const emit = defineEmits(['updateName'])

const updateName = function () {
  emit('updateName')
}
```

```vue
<button @click="updateName">이름 변경</button>
```

**2단계** — `ParentChild`에서 이벤트 수신 후, 다시 위로 발신

```js
// ParentChild.vue

const emit = defineEmits(['someEvent', 'emitArgs', 'updateName'])

const updateName = function () {
  emit('updateName')
}
```

```vue
<ParentGrandChild :my-msg="myMsg" @update-name="updateName" />
```

**3단계** — `Parent`에서 수신 후 실제 변수 변경

```js
// Parent.vue

const updateName = function () {
  name.value = 'Bella'
}
```

> 해당 변수를 props로 받는 **모든 컴포넌트가 자동 업데이트**된다. 이것이 props + emit 조합의 핵심이다.

### 2-7. ※주의※ 정적 & 동적 props (p.69)

```vue
<SomeComponent num-props="1" />
<SomeComponent :num-props="1" />
```

| 코드 | 전달되는 값 |
|---|---|
| `num-props="1"` | 정적 props — **문자열 `"1"`** |
| `:num-props="1"` | 동적 props — **숫자 `1`** |

숫자·불리언·배열·객체를 넘길 때 `v-bind`를 빼먹으면 전부 문자열이 된다. 자주 걸리는 함정이다.

### 2-8. ※주의※ 객체 선언 방식을 권장하는 이유 (p.70)

- 컴포넌트를 **가독성 좋게 문서화**하는 데 도움이 된다.
- 다른 개발자가 **잘못된 타입을 전달**할 때 브라우저 콘솔에 경고를 출력하도록 한다.
- 추가로 props에 대한 **유효성 검사**로써 활용 가능하다.

```js
defineProps({
  propB: [String, Number],
  propC: {
    type: String,
    required: true
  },
  propD: {
    type: Number,
    default: 10
  }
})
```

참고: <https://vuejs.org/guide/components/props.html#prop-validation>

### 2-9. emit 이벤트의 객체 선언 문법 (p.71)

emit 이벤트 또한 객체 구문으로 선언하면 **유효성 검사**를 할 수 있다.

```js
const emit = defineEmits({
  click: null,
  submit: ({ email, password }) => {
    if (email && password) {
      return true
    } else {
      console.warn('submit 이벤트가 올바르지 않음')
      return false
    }
  }
})

const submitForm = function (email, password) {
  emit('submit', { email, password })
}
```

`click: null`처럼 검사가 필요 없으면 `null`을 쓴다.

참고: <https://vuejs.org/guide/components/events.html#events-validation>

---

## 3. Computed Properties

### 3-1. computed란 (p.74)

**"계산된 속성"을 정의하는 함수.** 미리 계산된 값을 사용하여 템플릿에서 표현식을 단순하게 하고 불필요한 반복 연산을 줄인다.

### 3-2. 기본 예시 (p.75-76)

**Before** — 템플릿에 로직이 들어간 경우

```js
const todos = ref([
  { text: 'Vue 실습' },
  { text: '자격증 공부' },
  { text: 'TIL 작성' }
])
```

```vue
<h2>남은 할 일</h2>
<p>{{ todos.length > 0 ? '아직 남았다' : '퇴근!' }}</p>
```

문제점:

- 템플릿이 복잡해지며, todos에 따라 계산을 수행하게 된다.
- 만약 이 계산을 템플릿에서 여러 번 사용하는 경우 **반복이 발생**한다.

**After** — computed 적용

```js
import { ref, computed } from 'vue'

const restOfTodos = computed(() => {
  return todos.value.length > 0 ? '아직 남았다' : '퇴근!'
})
```

```vue
<h2>남은 할 일</h2>
<p>{{ restOfTodos }}</p>
```

> 반응형 데이터를 포함하는 복잡한 로직의 경우 computed를 활용하여 미리 값을 계산하고, 계산된 값을 사용한다.

### 3-3. computed 특징 (p.77)

- 반환되는 값은 **computed ref**이며, 일반 ref와 유사하게 계산된 결과를 `.value`로 참조할 수 있다. (템플릿에서는 `.value` 생략 가능)
- computed 속성은 **의존된 반응형 데이터를 자동으로 추적**한다.
- **의존하는 데이터가 변경될 때만 재평가**된다. 위 예시에서 `restOfTodos`의 계산은 `todos`에 의존하므로, `todos`가 변경될 때만 `restOfTodos`가 업데이트된다.

### 3-4. computed vs. methods (p.79-84)

method로도 동일한 기능을 만들 수는 있다.

```js
const getRestOfTodos = function () {
  return todos.value.length > 0 ? '아직 남았다' : '퇴근!'
}
```

```vue
<p>{{ getRestOfTodos() }}</p>
```

**결정적 차이는 캐싱이다.**

| | computed | method |
|---|---|---|
| 캐싱 | 의존된 반응형 데이터를 기반으로 **캐시(cached)됨** | 없음 |
| 재실행 시점 | 의존하는 데이터가 **변경된 경우에만** 재평가 | **다시 렌더링될 때마다 항상** 함수를 실행 |
| 실행 트리거 | 의존 데이터 변경 시 자동 업데이트 | 호출해야만 실행 |

> 의존된 반응형 데이터가 변경되지 않는 한, 이미 계산된 결과에 대한 여러 참조는 다시 평가할 필요 없이 **이전에 계산된 결과를 즉시 반환**한다.

**Cache(캐시)** 란 데이터나 결과를 일시적으로 저장해두는 임시 저장소다. 이후 같은 데이터나 결과를 다시 계산하지 않고 빠르게 접근할 수 있도록 한다. (브라우저가 방문했던 페이지의 이미지 등을 캐시에 저장해 두었다가 재접속 시 `(memory cache)`로 즉시 반환하는 것과 같은 원리)

**적절한 사용처**

| | 사용처 |
|---|---|
| computed | 의존하는 데이터에 따라 결과가 바뀌는 계산된 값을 만들 때. 동일한 의존성을 가진 여러 곳에서 사용할 때 캐싱하여 중복 계산 방지 |
| method | 단순히 특정 동작을 수행하는 함수를 정의할 때. 데이터 의존 여부와 관계없이 항상 동일한 결과를 반환하는 함수 |

> 무조건 computed만 사용하는 것이 아니라, **사용 목적과 상황에 맞게 computed와 method를 적절히 조합**하여 사용한다.

### 3-5. ※주의※ computed의 반환 값은 변경하지 말 것 (p.96)

- computed의 반환 값은 의존하는 데이터의 **파생된 값**이다. 이미 계산이 완료된 값이다.
- 일종의 **snapshot**이며, 의존하는 데이터가 변경될 때만 새 snapshot이 생성된다.
- 계산된 값은 **읽기 전용으로 취급**되어야 하며 변경되어서는 안 된다.
- 대신 새 값을 얻으려면 **의존하는 데이터를 업데이트**해야 한다.

### 3-6. ※주의※ 원본 배열을 변경하지 말 것 (p.97)

computed에서 `reverse()`와 `sort()`를 사용할 때는 **원본 배열을 변경하기 때문에** 복사본을 만들어서 진행해야 한다.

```js
// X — 원본 배열이 뒤집힘
return numbers.reverse()

// O — 복사본을 만들어 뒤집음
return [...numbers].reverse()
```

---

## 4. Watchers

### 4-1. watch란 (p.87-88)

하나 이상의 반응형 데이터를 **감시**하고, 감시하는 데이터가 변경되면 **콜백 함수를 호출**한다.

```js
watch(source, (newValue, oldValue) => {
})
```

| 인자 | 설명 |
|---|---|
| 첫 번째 (`source`) | watch가 감시하는 대상 (반응형 변수, 값을 반환하는 함수 등) |
| 두 번째 (callback function) | `source`가 변경될 때 호출되는 콜백 함수 |
| └ `newValue` | 감시하는 대상이 변화된 값 |
| └ `oldValue` (optional) | 감시하는 대상의 기존 값 |

### 4-2. 기본 동작 (p.89)

```vue
<button @click="count++">Add 1</button>
<p>Count: {{ count }}</p>
```

```js
const count = ref(0)

watch(count, (newValue, oldValue) => {
  console.log(`newValue: ${newValue}, oldValue: ${oldValue}`)
})
```

```text
newValue: 1, oldValue: 0
newValue: 2, oldValue: 1
newValue: 3, oldValue: 2
```

### 4-3. 활용 예시 (p.90-91)

감시하는 변수에 변화가 생겼을 때 **연관 데이터를 업데이트**하는 패턴.

```vue
<input v-model="message">
<p>Message Length: {{ messageLength }}</p>
```

```js
const message = ref('')
const messageLength = ref(0)

watch(message, (newValue) => {
  messageLength.value = newValue.length
})
```

### 4-4. 여러 source를 감시하기 (p.92)

배열을 활용한다. 콜백의 인자도 배열로 구조 분해된다.

```js
watch([foo, bar], ([newFoo, newBar], [prevFoo, prevBar]) => {
})
```

### 4-5. computed vs. watch (p.94)

| | computed | watch |
|---|---|---|
| **동작** | 의존하는 데이터 속성의 계산된 값을 반환 | 특정 데이터 속성의 변화를 감지하고 작업을 수행 (side-effects) |
| **사용 목적** | 계산한 값을 캐싱하여 재사용 | 데이터 변화에 따른 특정 작업을 수행 |
| **사용 예시** | 연산된 길이, 필터링된 목록 계산 등 | DOM 변경, 다른 비동기 작업 수행, 외부 API 연동 등 |

> computed와 watch **모두 의존(감시)하는 원본 데이터를 직접 변경하지 않는다.**

기억할 한 줄: **값을 만들면 computed, 일을 시키면 watch.**

---

## 5. Lifecycle Hooks

### 5-1. 개념 (p.100-101)

Vue 인스턴스의 **생애주기 동안 특정 시점에 실행되는 함수**. 인스턴스의 생애 주기 중간중간에 함수를 제공하여, 개발자가 특정 단계에서 원하는 로직을 작성할 수 있도록 한다.

참고: <https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram>

### 5-2. onMounted (p.102)

Vue 컴포넌트 인스턴스가 **초기 렌더링 및 DOM 요소 생성이 완료된 후** 특정 로직을 수행한다.

```js
import { ref, onMounted } from 'vue'

onMounted(() => {
  console.log('mounted')
})
```

### 5-3. onUpdated (p.103-104)

반응형 데이터의 변경으로 인해 컴포넌트의 **DOM이 업데이트된 후** 특정 로직을 수행한다.

```vue
<button @click="count++">Add 1</button>
<p>Count: {{ count }}</p>
<p>{{ message }}</p>
```

```js
import { ref, onMounted, onUpdated } from 'vue'

const count = ref(0)
const message = ref(null)

onUpdated(() => {
  message.value = 'updated!'
})
```

### 5-4. 특징 (p.105)

- Vue는 Lifecycle Hooks에 등록된 콜백 함수들을 **인스턴스와 자동으로 연결**한다.
- 이렇게 동작하려면 hooks 함수들은 **반드시 동기적으로 작성**되어야 한다.
- 가장 일반적으로 사용되는 것은 **`onMounted`, `onUpdated`, `onUnmounted`**.

참고: <https://vuejs.org/api/composition-api-lifecycle.html>

---

## 6. Virtual DOM

### 6-1. 개념 (p.107)

가상의 DOM을 **메모리에 저장**하고 실제 DOM과 동기화하는 프로그래밍 개념.

- 실제 DOM과의 **변경 사항 비교**를 통해 변경된 부분만 실제 DOM에 적용하는 방식이다.
- 웹 애플리케이션의 성능을 향상시키기 위한 Vue의 **내부 렌더링 기술**이다.

```html
<!DOCTYPE html>
<html lang="en">
<head>
</head>
<body>
  <div id="app"></div>   <!-- 이 안쪽이 Vue의 영역 (Virtual DOM) -->
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

### 6-2. 내부 렌더링 과정 (p.108)

```text
컴포넌트 + 반응형 상태
   ↓ 컴파일
가상 DOM 트리
   ↓ 마운트 / 패치
실제 DOM
   ↑ 반응형 상태가 변경되면 다시 렌더 → 새 가상 DOM 트리와 비교(패치)
```

### 6-3. 장점 (p.109)

| 항목 | 설명 |
|---|---|
| **효율성** | 실제 DOM 조작을 최소화하고, 변경된 부분만 업데이트하여 성능 향상 |
| **반응성** | 데이터의 변경을 감지하고, Virtual DOM을 효율적으로 갱신하여 UI를 자동으로 업데이트 |
| **추상화** | 개발자는 실제 DOM 조작을 Vue에게 맡기고, 컴포넌트와 템플릿을 활용하는 추상화된 방식으로 UI를 구성·관리 |

### 6-4. ※주의※ 실제 DOM에 직접 접근하지 말 것 (p.110)

- JavaScript에서 사용하는 DOM 접근 관련 메서드 **사용 금지** — `querySelector`, `createElement`, `addEventListener` 등
- Vue의 `ref()`와 Lifecycle Hooks 함수를 사용해 **간접적으로 접근하여 조작**할 것

### 6-5. 직접 DOM 엘리먼트에 접근해야 하는 경우 (p.111)

`ref` **속성**을 사용하여 특정 DOM 엘리먼트에 직접적인 참조를 얻을 수 있다.

```vue
<template>
  <input ref="input">
</template>

<script setup>
import { ref, onMounted } from 'vue'

const input = ref(null)

onMounted(() => {
  console.log(input.value)
})
</script>
```

> 템플릿의 `ref="input"` 속성 이름과 `const input = ref(null)`의 변수 이름이 **일치**해야 연결된다. 또한 DOM이 생성된 후여야 하므로 `onMounted` 안에서 접근한다.

---

## 7. 정리 체크리스트

- [ ] props가 왜 필요한지, 없으면 무엇이 문제인지 설명할 수 있다
- [ ] One-Way Data Flow가 무엇이고 왜 단방향인지 말할 수 있다
- [ ] `defineProps()`의 두 가지 선언 방식을 쓰고, 객체 방식이 권장되는 이유 3가지를 안다
- [ ] props와 emit의 이름 표기 규칙(전달/수신은 kebab-case, 선언/발신은 camelCase)을 헷갈리지 않는다
- [ ] `num-props="1"`과 `:num-props="1"`의 차이를 안다
- [ ] `defineEmits()`가 왜 필요한지(`<script>`에서 `$emit` 접근 불가) 설명할 수 있다
- [ ] 손자 컴포넌트에서 조부모의 데이터를 바꾸는 emit 릴레이를 직접 짤 수 있다
- [ ] computed와 method의 차이를 캐싱 관점에서 설명할 수 있다
- [ ] computed와 watch를 언제 각각 쓰는지 구분할 수 있다
- [ ] computed 안에서 `reverse()`를 쓸 때 주의점을 안다
- [ ] `onMounted`와 `onUpdated`의 실행 시점을 구분한다
- [ ] Virtual DOM이 무엇이며, 왜 `querySelector`를 쓰면 안 되는지 안다

## 8. 복습 문제

1. **자식 컴포넌트에서 `props.myMsg = 'new'`를 실행하면 어떻게 되는가?**
   <details><summary>답</summary>변경되지 않는다. props는 하향식 단방향 바인딩이므로 자식에서의 변경은 시도해서는 안 되며 불가능하다. 부모의 데이터를 바꾸려면 `$emit`으로 부모에게 변경을 요청해야 한다.</details>

2. **`<Child count="5" />`로 넘긴 값을 자식에서 `defineProps({ count: Number })`로 받으면 왜 경고가 뜨는가?**
   <details><summary>답</summary>`v-bind` 없이 넘기면 정적 props가 되어 문자열 `"5"`가 전달된다. 선언된 타입 `Number`와 맞지 않아 콘솔 경고가 출력된다. `:count="5"`로 써야 숫자 5가 전달된다.</details>

3. **`{{ getRestOfTodos() }}`(method)와 `{{ restOfTodos }}`(computed)는 결과가 같은데 무엇이 다른가?**
   <details><summary>답</summary>computed는 의존하는 반응형 데이터가 변경될 때만 재평가되고 그 외에는 캐시된 결과를 즉시 반환한다. method는 리렌더링이 발생할 때마다 매번 함수를 실행한다.</details>

4. **입력값이 바뀔 때마다 서버에 검색 요청을 보내려 한다. computed와 watch 중 무엇을 쓰는가?**
   <details><summary>답</summary>watch. 값을 계산해 반환하는 게 아니라 데이터 변화에 따라 부수 효과(side-effect)인 비동기 API 호출을 수행하는 상황이기 때문이다.</details>

5. **`ParentGrandChild`에서 `Parent`의 `name`을 바꾸려면 몇 번의 emit이 필요한가?**
   <details><summary>답</summary>2번. `ParentGrandChild → ParentChild`, `ParentChild → Parent`로 한 단계씩 릴레이해야 한다. 이벤트는 단계를 건너뛸 수 없다.</details>

6. **`onMounted` 밖에서 `input.value`에 접근하면 왜 `null`인가?**
   <details><summary>답</summary>`setup` 실행 시점에는 아직 DOM 요소가 생성되지 않았기 때문이다. 초기 렌더링과 DOM 생성이 완료된 후 호출되는 `onMounted` 안에서 접근해야 한다.</details>

---

<!-- 작성 메모: p.1-37은 슬라이드 이미지를 직접 판독, p.38-112는 OCR(tesseract kor+eng)로 추출 후 재구성.
     코드 내 한글 문자열 리터럴(예: '자격증 공부')은 OCR 특성상 원본과 미세한 차이가 있을 수 있으므로,
     그대로 옮겨 적을 때는 해당 슬라이드를 한 번 확인할 것. 코드 구조와 API 시그니처는 검증 완료. -->
