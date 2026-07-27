# Vue.js — State Management & Routing

> 출처: `16기_데이터트랙_0727_2_StateManagement.pdf` (총 106페이지)
> 범위: State Management / Pinia / Local Storage / Routing / Vue Router / Navigation Guard

## 한눈에 보기

- 컴포넌트가 늘어날 때 **props와 emit만으로는 왜 무너지는지**, 그 지점을 설명할 수 있다.
- **Pinia**의 store / state / getters / actions가 각각 Vue의 무엇과 대응되는지 안다.
- 새로고침해도 상태를 유지하려면 무엇을 붙여야 하는지(`pinia-plugin-persistedstate`) 안다.
- SPA에서 **왜 라우터가 필요한지**, 없으면 무엇이 안 되는지 말할 수 있다.
- `RouterLink` / `RouterView` / `router/index.js`의 역할 분담을 이해하고, 동적 경로와 중첩 라우팅을 작성할 수 있다.

## 목차

1. [State Management](#1-state-management) (p.4-14)
2. [Pinia](#2-pinia) (p.16-47)
3. [Routing 개요](#3-routing-개요) (p.48-53)
4. [Vue Router](#4-vue-router) (p.55-90)
5. [참고 주제](#5-참고-주제) (p.92-105)
6. [정리 체크리스트](#6-정리-체크리스트)
7. [복습 문제](#7-복습-문제)

---

## 1. State Management

### 1-1. 상태 관리란 (p.6)

Vue 컴포넌트는 **이미 반응형 상태를 관리하고 있다.**

> **상태(State) === 데이터**

### 1-2. 컴포넌트 구조의 단순화 (p.7-8)

컴포넌트 하나를 세 조각으로 쪼개서 보면 이렇게 된다.

| 구성 | 설명 | Vue에서의 대응 |
|---|---|---|
| **상태(State)** | 앱 구동에 필요한 기본 데이터 | `ref()` |
| **뷰(View)** | 상태를 선언적으로 매핑하여 시각화 | `<template>` |
| **기능(Actions)** | 뷰에서 사용자 입력에 대해 반응적으로 상태를 변경할 수 있게 정의된 동작 | `function()` |

```vue
<template>
  <!-- 뷰(View) -->
  <div>{{ count }}</div>
</template>

<script setup>
import { ref } from 'vue'

// 상태(State)
const count = ref(0)

// 기능(Actions)
const increment = function () {
  count.value++
}
</script>
```

이것이 **"단방향 데이터 흐름"의 간단한 표현**이다.

```text
State ──→ View ──→ Actions
  ↑                   │
  └───────────────────┘
```

### 1-3. 단순성이 무너지는 시점 (p.9-11)

문제는 **"여러 컴포넌트가 상태를 공유할 때"** 생긴다. 두 가지 경우다.

**1. 여러 뷰가 동일한 상태에 종속되는 경우**

- 해결하려면 공유 상태를 공통 조상 컴포넌트로 **"끌어올린" 다음 props로 전달**해야 한다.
- 하지만 **계층 구조가 깊어질 경우 비효율적이고 관리가 어려워진다.** (props drilling)

**2. 서로 다른 뷰의 기능이 동일한 상태를 변경시켜야 하는 경우**

- 발신(emit)된 이벤트를 통해 상태의 **여러 복사본을 변경 및 동기화**해야 한다.
- 마찬가지로 **관리의 패턴이 깨지기 쉽고 유지 관리할 수 없는 코드**가 된다.

> 앞 차시에서 배운 props/emit 릴레이가 바로 이 지점에서 한계에 부딪힌다. 3단계만 되어도 손자→조부모 emit을 두 번 거쳐야 했던 걸 떠올리면 이해가 빠르다.

### 1-4. 해결책 (p.12-14)

각 컴포넌트의 **공유 상태를 추출하여, 전역에서 참조할 수 있는 저장소(중앙 저장소)에서 관리**한다.

```text
        ┌──────────────┐
        │  중앙 저장소  │   ← 모든 컴포넌트가 직접 접근
        └──────────────┘
         ↑     ↑     ↑
      [A]     [B]     [C]     (트리 깊이와 무관)
```

컴포넌트 트리는 하나의 큰 View가 되고, 모든 컴포넌트는 **트리 계층 구조에 관계 없이** 상태에 접근하거나 기능을 사용할 수 있다.

> Vue의 공식 상태 관리 라이브러리 === **"Pinia"**

---

## 2. Pinia

### 2-1. 설치와 프로젝트 구조 변화 (p.18-20)

Vue 프로젝트 빌드 시 Pinia 라이브러리를 추가한다.

```text
? Select features to include in your project:
  ◉ Pinia (state management)
```

추가되면 **`stores` 폴더가 신규 생성**된다.

```text
src/
├── assets/
├── components/
├── stores/
│   └── counter.js     ← 신규
├── App.vue
└── main.js
```

### 2-2. Pinia 구성 요소 5가지 (p.22-29)

기준이 되는 `counter.js` 전체 코드는 아래와 같다. 이 하나에 구성 요소가 전부 들어 있다.

```js
// stores/counter.js

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  const increment = function () {
    count.value++
  }
  return { count, doubleCount, increment }
})
```

**1. store** — 중앙 저장소. 모든 컴포넌트가 공유하는 상태, 기능 등이 작성된다.

- `defineStore()`의 **반환 값의 이름은 `use`와 `store`를 사용하는 것을 권장** (`useCounterStore`)
- `defineStore()`의 **첫 번째 인자는 애플리케이션 전체에 걸쳐 사용하는 store의 고유 ID** (`'counter'`)

**2. state** — 반응형 상태(데이터). **`ref()` === state**

**3. getters** — 계산된 값. **`computed()` === getters**

**4. actions** — 메서드. **`function()` === actions**

**5. plugin** — 애플리케이션의 상태 관리에 필요한 추가 기능을 제공하거나 확장하는 도구나 모듈. 상태 관리를 더욱 간편하고 유연하게 만들어주며, 패키지 매니저로 설치 이후 별도 설정을 통해 추가된다.

> **정리** — Pinia는 `store`라는 저장소를 가진다. store는 **state, getters, actions**로 이루어지며 각각 **`ref()`, `computed()`, `function()`과 동일**하다.

### 2-3. Setup Stores의 반환 값 (p.27)

- Pinia의 상태들을 사용하려면 **반드시 반환(`return`)해야 한다.**
- store에서는 **공유하지 않는 private한 상태 속성을 가지지 않는다.**

즉 `return { count, doubleCount, increment }`에서 빠뜨린 것은 컴포넌트에서 쓸 수 없다. 자주 하는 실수다.

### 2-4. 컴포넌트에서 활용하기 (p.31-34)

#### State

각 컴포넌트 깊이에 관계 없이 store의 state에 접근하여 **직접 읽고 쓸 수 있다.**

```js
// App.vue

import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()

// state 참조 및 변경
console.log(store.count)
const newNumber = store.count + 1
```

```vue
<template>
  <div>
    <p>state : {{ store.count }}</p>
  </div>
</template>
```

> 만약 store에 state를 정의하지 않았다면 **컴포넌트에서 새로 추가할 수 없다.**

#### Getters

store의 모든 getters 또한 state처럼 직접 접근할 수 있다.

```js
console.log(store.doubleCount)
```

```vue
<p>getters : {{ store.doubleCount }}</p>
```

#### Actions

store의 모든 actions 또한 직접 접근 및 호출할 수 있다.

```js
// actions 호출
store.increment()
```

```vue
<button @click="store.increment()">+++</button>
```

> **getters와 달리** actions는 state 조작, 비동기, API 호출이나 다른 로직을 진행할 수 있다.

Vue devtools의 Pinia 탭에서 state와 getters의 실제 값을 확인할 수 있다.

### 2-5. Local Storage (p.36-38)

**Local Storage**: 브라우저 내에 key-value 형태로 저장하는 웹 스토리지 객체.

특징:

- 페이지를 새로 고침하고 **브라우저를 다시 실행해도 데이터가 유지**된다.
- **쿠키와 다르게 네트워크 요청 시 서버로 전송되지 않는다.**
- 여러 탭이나 창 간에 데이터를 공유할 수 있다.

사용 목적: 사용자 설정, 상태 정보, 캐시 데이터 등을 클라이언트 측에서 보관하여 웹사이트의 성능을 향상시키고 사용자 경험을 개선하기 위함.

### 2-6. pinia-plugin-persistedstate (p.39-43)

Pinia의 **플러그인 중 하나.** 웹 애플리케이션의 상태(state)를 브라우저의 local storage나 session storage에 **영구적으로 저장하고 복원**하는 기능을 제공한다.

공식 문서: <https://prazdevs.github.io/pinia-plugin-persistedstate/>

**설정 1단계 — `main.js`에 등록**

```js
// main.js

import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const app = createApp(App)
const pinia = createPinia()

pinia.use(piniaPluginPersistedstate)
app.use(pinia)

app.mount('#app')
```

**설정 2단계 — `defineStore()`의 3번째 인자로 관련 객체 추가**

```js
export const useCounterStore = defineStore('counter', () => {
  return { count, doubleCount, increment }
}, { persist: true })
```

**확인** — 개발자도구 > Application > Local Storage에서 저장되는 state를 볼 수 있다.

### 2-7. 모든 데이터를 store에서 관리해야 할까? (p.46-47)

- Pinia를 사용한다고 해서 **모든 데이터를 store에 넣어야 하는 것은 아니다.**
- **pass props, emit event를 함께 사용**하여 애플리케이션을 구성해야 한다.
- Pinia는 공유된 상태를 관리하는 데 유용하지만, **구조적인 개념에 대한 이해와 시작하는 비용이 크다.**
- 애플리케이션이 단순하다면 **Pinia가 없는 것이 더 좋을 수 있다.**
- 그러나 **중대형 규모의 SPA**를 구축하는 경우 Pinia는 자연스럽게 선택할 수 있는 단계가 온다.

> 결과적으로 적절한 상황에서 활용했을 때 Pinia의 장점을 극대화할 수 있다.

---

## 3. Routing 개요

### 3-1. Routing이란 (p.50)

**네트워크에서 경로를 선택하는 프로세스.** 웹 애플리케이션에서는 **다른 페이지 간의 전환과 경로를 관리하는 기술**을 뜻한다.

### 3-2. SSR vs CSR에서의 Routing (p.51-52)

| | SSR | CSR |
|---|---|---|
| 수행 위치 | **서버 측** | **클라이언트 측** |
| 동작 | 서버가 사용자가 방문한 URL 경로를 기반으로 응답을 전송 | 클라이언트의 JavaScript가 새 데이터를 동적으로 가져옴 |
| 페이지 전환 | 브라우저가 서버로부터 HTML 응답을 수신하고 **새 HTML로 전체 페이지를 다시 로드** | **전체 페이지를 다시 로드하지 않음** |

### 3-3. CSR에서 Routing이 없다면 (p.53)

- 유저가 **URL을 통한 페이지의 변화를 감지할 수 없다.**
- 페이지가 무엇을 렌더링 중인지에 대한 **상태를 알 수 없다.**
  - URL이 1개이기 때문에 **새로 고침 시 처음 페이지로 되돌아간다.**
  - 링크를 공유할 시 **첫 페이지만 공유 가능**하다.
- 브라우저의 **뒤로 가기 기능을 사용할 수 없다.**

> 페이지는 1개이지만, 주소에 따라 여러 컴포넌트를 새로 렌더링하여 **마치 여러 페이지를 사용하는 것처럼 보이도록** 해야 한다. 이것이 SPA 라우터의 존재 이유다.

---

## 4. Vue Router

### 4-1. 사전 준비와 구조 변화 (p.57-60)

Vue 공식 라우터. 프로젝트 생성 시 Router를 추가한다.

```text
? Select features to include in your project:
  ◉ Router (SPA development)
```

세 가지가 달라진다.

1. `App.vue` 코드 변화
2. **`router` 폴더 신규 생성**
3. **`views` 폴더 신규 생성**

```text
src/
├── assets/
├── components/
├── router/
│   └── index.js       ← 신규
├── views/             ← 신규
│   ├── AboutView.vue
│   └── HomeView.vue
├── App.vue
└── main.js
```

### 4-2. RouterLink와 RouterView (p.61-63)

**RouterLink**

- **페이지를 다시 로드하지 않고 URL을 변경**하여 URL 관리 및 관련 기능을 처리
- HTML의 `<a>` 태그를 렌더링한다

**RouterView**

- RouterLink URL에 해당하는 **컴포넌트를 표시**
- 원하는 곳에 배치하여 컴포넌트를 레이아웃에 표시할 수 있다

```vue
<template>
  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </header>

  <RouterView />
</template>
```

역할 분담을 한 줄로: **RouterLink는 "어디로 갈지", RouterView는 "어디에 그릴지".**

### 4-3. router/index.js와 views (p.64-65)

**`router/index.js`** — 라우팅에 관련된 정보 및 설정이 작성되는 곳. router의 **URL과 컴포넌트를 매핑**한다.

**`views` 폴더** — RouterView 위치에 렌더링할 컴포넌트를 배치한다.

- 기존 `components` 폴더와 **기능적으로 다른 것은 없으며 단순 분류의 의미**로 구성됨
- 일반 컴포넌트와 구분하기 위해 컴포넌트 이름을 **`View`로 끝나도록 작성하는 것을 권장**

### 4-4. Basic Routing (p.67-69)

**1. `index.js`에 라우터 관련 설정 작성** (주소, 이름, 컴포넌트)

```js
// index.js

const router = createRouter({
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
  ]
})
```

**2. RouterLink의 `to` 속성으로 `index.js`에서 정의한 주소 값(`path`)을 사용**

```vue
<RouterLink to="/">Home</RouterLink>
<RouterLink to="/about">About</RouterLink>
```

**3. RouterLink 클릭 시 경로와 일치하는 컴포넌트가 RouterView에서 렌더링됨**

### 4-5. Named Routes (p.71-73)

경로에 **이름을 지정**하는 라우팅.

- `name` 속성 값에 경로에 대한 이름을 지정한다.
- 경로에 연결하려면 RouterLink에 **`v-bind`를 사용해 `to` props를 객체로 전달**한다.

```js
const router = createRouter({
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
  ]
})
```

```vue
<RouterLink :to="{ name: 'home' }">Home</RouterLink>
<RouterLink :to="{ name: 'about' }">About</RouterLink>
```

**장점**

- 하드 코딩된 URL을 사용하지 않아도 된다
- URL 입력 시 오타 방지

문서: <https://router.vuejs.org/guide/essentials/named-routes.html>

### 4-6. Dynamic Route Matching (p.75-81)

**URL의 일부를 변수로 사용하여 경로를 동적으로 매칭**하는 것.

주어진 패턴 경로를 동일한 컴포넌트에 매핑해야 하는 경우 활용한다. 예를 들어 모든 사용자의 ID를 활용하여 프로필 페이지 URL을 설계한다면 `/user/1`, `/user/2`, `/user/3`... 일정한 패턴의 URL 작성을 반복해야 한다.

**1단계 — `views` 폴더 내 `UserView` 컴포넌트 작성**

```vue
<!-- UserView.vue -->

<template>
  <div>
    <h1>UserView</h1>
  </div>
</template>
```

**2단계 — 라우트 등록. 매개변수는 콜론(`:`)으로 표기**

```js
// index.js

import UserView from '../views/UserView.vue'

const router = createRouter({
  routes: [
    {
      path: '/user/:id',
      name: 'user',
      component: UserView
    },
  ]
})
```

**3단계 — RouterLink 작성. 매개변수는 객체의 `params` 속성에 객체 타입으로 전달**

```js
import { ref } from 'vue'

const userId = ref(1)
```

```vue
<RouterLink :to="{ name: 'user', params: { 'id': userId } }">User</RouterLink>
```

> **주의** — 객체의 key 이름과 `index.js`에서 지정한 **매개변수 이름이 같아야 한다.** (`:id` ↔ `'id'`)

**4단계 — 경로가 일치하면 라우트의 매개변수는 컴포넌트에서 `$route.params`로 참조 가능**

```vue
<template>
  <div>
    <h1>UserView</h1>
    <h2>{{ $route.params.id }}번 User 페이지</h2>
  </div>
</template>
```

**5단계 — `useRoute()` 사용 (권장)**

`useRoute()` 함수를 사용해 스크립트 내에서 반응형 변수에 할당한 후 템플릿에 출력하는 것을 권장한다. 템플릿에서 `$route`를 사용하는 것과 동일하다.

```js
// UserView.vue

import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const userId = ref(route.params.id)
```

문서: <https://router.vuejs.org/guide/essentials/dynamic-matching.html>

### 4-7. Programmatic Navigation (p.83-90)

**RouterLink 대신 JavaScript를 사용해 페이지를 이동하는 것.** router의 인스턴스 메서드를 사용해, RouterLink가 `<a>` 태그를 만드는 것처럼 프로그래밍으로 네비게이션 작업을 수행한다.

| 메서드 | 역할 |
|---|---|
| `router.push()` | 다른 위치로 이동하기 |
| `router.replace()` | 현재 위치 바꾸기 |

#### router.push()

- 다른 URL로 이동하는 메서드
- **새 항목을 history stack에 추가**하므로, 사용자가 브라우저 뒤로 가기 버튼을 클릭하면 이전 URL로 이동할 수 있다
- RouterLink를 클릭했을 때 **내부적으로 호출되는 메서드**이므로, RouterLink를 클릭하는 것은 `router.push()`를 호출하는 것과 같다

| 선언적 표현 | 프로그래밍적 표현 |
|---|---|
| `<RouterLink :to="...">` | `router.push(...)` |

**활용 예** — UserView에서 HomeView로 이동하는 버튼 만들기

```js
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()

const goHome = function () {
  router.push({ name: 'home' })
}
```

```vue
<button @click="goHome">홈으로</button>
```

> `useRoute()`는 **현재 경로 정보를 읽을 때**, `useRouter()`는 **이동시킬 때**. 이름이 비슷해서 헷갈리기 쉽다.

**인자 활용 4가지**

```js
router.push('/users/1')
router.push({ path: '/users/2' })
router.push({ name: 'user', params: { id: '3' } })
router.push({ path: '/register', query: { plan: 'private' } })
```

문서: <https://router.vuejs.org/guide/essentials/navigation.html>

---

## 5. 참고 주제

### 5-1. Nested Routes (p.94-101)

애플리케이션의 UI는 여러 레벨 깊이로 **중첩된 컴포넌트**로 구성되기도 한다. 이 경우 URL의 세그먼트를 컴포넌트의 구조에 따라 변경되도록 이 관계를 표현할 수 있다.

```text
/user/:id/profile          /user/:id/posts
┌──────────────┐           ┌──────────────┐
│ User         │           │ User         │
│  ┌─────────┐ │           │  ┌─────────┐ │
│  │ Profile │ │           │  │ Posts   │ │
│  └─────────┘ │           │  └─────────┘ │
└──────────────┘           └──────────────┘
```

**`children` 옵션**은 배열 형태로 필요한 만큼 중첩 관계를 표현할 수 있다.

```js
import UserHome from '@/components/UserHome.vue'

{
  path: '/user/:id',
  component: UserView,
  children: [
    { path: '', name: 'user', component: UserHome },
    { path: 'profile', name: 'user-profile', component: UserProfile },
    { path: 'posts', name: 'user-posts', component: UserPosts }
  ]
}
```

> 중첩된 Named Routes를 다룰 때는 일반적으로 **"하위 경로에만 이름을 지정"** 한다. 이렇게 하면 `/user/:id`로 이동했을 때 항상 중첩된 경로가 표시된다.

부모 컴포넌트에는 자식을 그릴 `RouterView`가 또 필요하다.

```vue
<!-- UserView.vue -->

<template>
  <div>
    <RouterLink :to="{ name: 'user-profile' }">Profile</RouterLink>
    <RouterLink :to="{ name: 'user-posts' }">Posts</RouterLink>

    <h1>UserView</h1>
    <h2>{{ userId }}번 User 페이지</h2>
    <hr>

    <RouterView />
  </div>
</template>
```

> **관점 전환** — 컴포넌트 간 부모-자식 관계 관점이 아니라, **URL에서의 중첩 관계를 표현하는 관점**으로 바라볼 것.

문서: <https://router.vuejs.org/guide/essentials/nested-routes.html>

### 5-2. Navigation Guard (p.103-104)

Vue router를 통해 특정 URL에 접근할 때 **다른 URL로 리다이렉트를 하거나 취소하여 내비게이션을 보호**하는 기능.

> 라우트 전환 시 **자동으로 실행되는 Hook**

| 종류 | 적용 범위 |
|---|---|
| **Globally** (전역 가드) | 애플리케이션 전역에서 모든 라우트 전환에 적용 |
| **Per-route** (라우터 가드) | 특정 라우트에만 적용 |
| **In-component** (컴포넌트 가드) | 컴포넌트 내에서만 적용 -> confirm으로 진짜? 하고 물어봄 ㅇㅇ|

문서: <https://router.vuejs.org/guide/advanced/navigation-guards.html>

### 5-3. Lazy Loading Routes (p.105)

```js
{
  path: '/about',
  name: 'about',
  component: () => import('../views/AboutView.vue')
}
```

- Vue 애플리케이션 **첫 빌드 시 해당 컴포넌트를 로드하지 않고, "해당 경로를 처음으로 방문할 때 컴포넌트를 로드"** 하는 것
- 앱을 빌드할 때 사용하는 모든 컴포넌트를 준비하면 컴포넌트의 크기에 따라 **페이지 로드 시간이 길어질 수 있기 때문**

`component: HomeView`(정적 import)와 `component: () => import(...)`(동적 import)의 차이가 핵심이다.

---

## 6. 정리 체크리스트

- [ ] State / View / Actions 삼각 구조를 그리고 Vue 문법과 대응시킬 수 있다
- [ ] props/emit만으로 상태를 공유할 때 무너지는 두 가지 경우를 설명할 수 있다
- [ ] `defineStore()`의 첫 번째 인자와 반환 값 이름 규칙을 안다
- [ ] state / getters / actions가 각각 `ref()` / `computed()` / `function()`임을 안다
- [ ] Setup Store에서 `return`을 빠뜨리면 어떻게 되는지 안다
- [ ] getters와 actions의 차이(비동기·API 호출 가능 여부)를 말할 수 있다
- [ ] Local Storage와 쿠키의 차이를 한 가지 이상 말할 수 있다
- [ ] `persist: true`를 어디에 쓰는지 안다
- [ ] SSR과 CSR의 라우팅 수행 위치 차이를 안다
- [ ] SPA에 라우터가 없으면 안 되는 것 3가지를 댈 수 있다
- [ ] RouterLink / RouterView / `router/index.js`의 역할을 구분한다
- [ ] Named Routes를 쓸 때 `:to`에 `v-bind`가 필요한 이유를 안다
- [ ] `/user/:id`의 값을 컴포넌트에서 꺼내는 두 가지 방법을 안다
- [ ] `useRoute()`와 `useRouter()`를 헷갈리지 않는다
- [ ] `children` 옵션으로 중첩 라우팅을 작성할 수 있다
- [ ] Lazy Loading Routes의 문법과 이유를 안다

## 7. 복습 문제

1. **`return { count, increment }`에서 `doubleCount`를 빠뜨리면 컴포넌트에서 `store.doubleCount`는 어떻게 되는가?**
   <details><summary>답</summary>`undefined`다. Setup Store에서는 반환한 것만 외부에 노출되며, 반환하지 않은 값은 store 내부의 private 속성처럼 동작한다. Pinia의 상태를 사용하려면 반드시 반환해야 한다.</details>

2. **`<RouterLink to="{ name: 'home' }">`가 동작하지 않는 이유는?**
   <details><summary>답</summary>`v-bind`가 빠졌다. 이렇게 쓰면 문자열 `"{ name: 'home' }"` 그대로 전달된다. 객체를 넘기려면 `:to="{ name: 'home' }"`로 써야 한다. 앞 차시의 정적/동적 props 함정과 같은 원리다.</details>

3. **`useRoute()`와 `useRouter()` 중 페이지를 이동시킬 때 쓰는 것은?**
   <details><summary>답</summary>`useRouter()`. `router.push()` 같은 인스턴스 메서드를 제공한다. `useRoute()`는 현재 경로 정보(`params`, `query` 등)를 읽을 때 쓴다.</details>

4. **Pinia를 쓰기 시작하면 props와 emit은 더 이상 필요 없는가?**
   <details><summary>답</summary>아니다. Pinia를 사용한다고 모든 데이터를 store에 넣어야 하는 것은 아니며, pass props와 emit event를 함께 사용해 구성해야 한다. 앱이 단순하다면 Pinia가 없는 편이 나을 수도 있다.</details>

5. **`path: '/user/:id'`로 등록했는데 `params: { userId: 1 }`로 전달하면?**
   <details><summary>답</summary>매칭되지 않는다. 객체의 key 이름과 `index.js`에서 지정한 매개변수 이름이 같아야 하므로 `params: { id: 1 }`이어야 한다.</details>

6. **`component: AboutView`와 `component: () => import('../views/AboutView.vue')`의 차이는?**
   <details><summary>답</summary>후자가 Lazy Loading이다. 첫 빌드 시 컴포넌트를 로드하지 않고 해당 경로를 처음 방문할 때 로드하므로, 초기 페이지 로드 시간을 줄일 수 있다.</details>

---

<!-- 작성 메모: 본 자료는 텍스트 레이어가 없는 이미지 전용 PDF(106p)로, OCR(tesseract kor+eng, 2200px)로 추출 후 재구성했다.
     코드 구조와 API 시그니처는 크롭 재OCR로 교차 검증했으나, 슬라이드 다이어그램(p.10-14, p.95)은
     텍스트로 옮기면서 배치를 단순화했으므로 원본 그림을 함께 볼 것.
     한글 UI 문자열(버튼 라벨 등)은 OCR 특성상 미세한 차이가 있을 수 있다. -->