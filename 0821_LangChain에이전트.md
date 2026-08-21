# LangChain 에이전트 실습 — LLM API부터 LangGraph, MCP·A2A, 관측성까지

> 출처: SSAFY `07_Langchain` 실습 코드 저장소 (Chapter1~4, 파이썬 파일 33개 + SKILL.md 1개) · 정리일: 2026-08-21
> 이번 차시는 강의 슬라이드 없이 **코드만** 제공됐다. 표기는 저장소 루트 기준 파일 경로다.
> 코드 인용은 핵심부만 발췌했고, 전체 흐름을 바꾸지 않는 범위에서 주석을 압축했다.

## 한눈에 보기

- 같은 LLM 호출을 `requests` → OpenAI SDK → LangChain 세 층위로 다시 쓸 수 있는가? 각 층이 무엇을 대신해 주는가?
- LCEL의 `|` 연산자가 잇는 것(Runnable)과 공통 실행 3종(`invoke` / `stream` / `batch`)을 설명할 수 있는가?
- `RunnableParallel` / `RunnablePassthrough` / `RunnableLambda`가 각각 언제 필요한가? dict가 파이프 사이에 들어가면 무슨 일이 생기는가?
- 도구 호출(tool calling)의 수동 루프에 필요한 세 가지 — `bind_tools`, `AIMessage.tool_calls`, `ToolMessage(tool_call_id=...)` — 를 짚을 수 있는가?
- 구조화 출력 2방식(`PydanticOutputParser` vs `with_structured_output`)의 원리 차이와 권장 기준은?
- 메모리 2전략 — `RunnableWithMessageHistory`(체인 외부 히스토리) vs LangGraph `State`+`checkpointer`(상태 내장) — 의 장단은?
- RAG 파이프라인 5단계(로딩→청킹→임베딩→벡터스토어→체인)를 각 단계의 클래스 이름과 함께 그릴 수 있는가?
- `chunk_size` / `chunk_overlap`이 트레이드오프하는 것은 무엇인가?
- LangGraph 3요소(State / Node / Edge)와 `add_messages` reducer의 역할은?
- `ToolNode` + `tools_condition`이 자동화하는 루프는 무엇이고, `create_agent`는 언제 쓰는가?
- Human-in-the-Loop: `interrupt_before`로 멈추고, `invoke(None)`으로 재개하고, `update_state(..., as_node='tools')`로 거부를 주입하는 흐름을 설명할 수 있는가?
- 멀티에이전트 2패턴 — 고정 파이프라인(Researcher→Writer) vs Supervisor 라우팅 — 의 차이는?
- MCP 서버의 세 구성요소(`@mcp.tool` / `@mcp.resource` / `@mcp.prompt`)와 두 transport(stdio / SSE)는?
- `MultiServerMCPClient.get_tools()`가 가져온 도구가 LangGraph의 ToolNode에 그대로 꽂히는 이유는?
- A2A의 발견 메커니즘(Agent Card, `/.well-known/agent-card.json`)과 실행 메커니즘(JSON-RPC `SendMessage` → `GetTask` 폴링)을 설명할 수 있는가?
- MCP와 A2A는 각각 "무엇과 무엇 사이"의 표준인가?
- 서브그래프의 State는 부모와 어떻게 격리되는가?
- `MemorySaver` / `SqliteSaver`의 차이와 Time-Travel(과거 체크포인트에서 재실행)의 원리는?
- Checkpointer(단기, thread 단위)와 Store(장기, thread 횡단)의 역할 분담은?
- 정적 병렬(fan-out/fan-in 엣지)과 동적 병렬(`Send` API)은 각각 언제 쓰는가?
- 하네스 엔지니어링: SKILL.md 파일 하나로 코드·모델 변경 없이 에이전트 행동을 바꾸는 구조를 설명할 수 있는가?
- Langfuse의 세 추적 도구 — `CallbackHandler`, `with_config`, `@observe` — 는 각각 어느 범위를 추적하는가?
- 평가 3방식(수동 / 규칙 기반 / LLM-as-a-Judge)과 다차원 RAG 평가(correctness·relevance·completeness)의 구성은?

## 목차

1. [큰 그림 — 이 코드들이 쌓아 올리는 스택](#큰-그림--이-코드들이-쌓아-올리는-스택)
2. [LLM API 세 층위](#llm-api-세-층위-chapter101-llm-api) (Chapter1/01-llm-api)
3. [LangChain 코어 — LCEL, 도구, 파서, 메모리](#langchain-코어--lcel-도구-파서-메모리-chapter102-langchain) (Chapter1/02-langchain)
4. [RAG 파이프라인](#rag-파이프라인-chapter103-rag--chapter206-rag-streamlit) (Chapter1/03-rag + Chapter2/06)
5. [LangGraph 기초 — 그래프로 만드는 에이전트](#langgraph-기초--그래프로-만드는-에이전트-chapter204-langgraph) (Chapter2/04-langgraph)
6. [멀티에이전트 패턴](#멀티에이전트-패턴-chapter205-multi-agent) (Chapter2/05-multi-agent)
7. [에이전트 생태계 표준 — MCP](#에이전트-생태계-표준-1--mcp-chapter301-mcp) (Chapter3/01-mcp)
8. [에이전트 생태계 표준 — A2A](#에이전트-생태계-표준-2--a2a-chapter302-a2a) (Chapter3/02-a2a)
9. [LangGraph 고급](#langgraph-고급-chapter303-langgraph-advanced) (Chapter3/03-langgraph-advanced)
10. [하네스 엔지니어링](#하네스-엔지니어링-chapter410-harness) (Chapter4/10-harness)
11. [관측성과 평가 — Langfuse](#관측성과-평가--langfuse-chapter411-observability) (Chapter4/11-observability)
12. [환경과 버전 메모](#환경과-버전-메모)
13. [코드에서 눈여겨볼 점](#코드에서-눈여겨볼-점-)

---

## 큰 그림 — 이 코드들이 쌓아 올리는 스택

이 저장소는 "LLM 한 번 호출"에서 시작해 "운영 가능한 에이전트 시스템"까지를 11개 모듈로 쌓는다. 각 모듈이 바로 앞 모듈의 남은 문제를 해결하는 구조라서, 순서 자체가 학습 지도다.

```text
Chapter1  01-llm-api      : HTTP 요청 → SDK → LangChain, 같은 호출의 세 층위
          02-langchain    : LCEL 체인, 도구 호출, 구조화 출력, 메모리 2전략
          03-rag          : 문서 로딩 → 청킹 → 임베딩 → 벡터스토어 → RAG 체인
Chapter2  04-langgraph    : State/Node/Edge, 조건 분기, ToolNode(ReAct), HITL
          05-multi-agent  : Researcher→Writer 파이프라인, Supervisor 라우팅
          06-rag-streamlit: RAG 체인을 Streamlit 챗봇 UI로
Chapter3  01-mcp          : FastMCP 서버 제작 + LangGraph 에이전트에 연결
          02-a2a          : LangGraph 에이전트를 A2A 프로토콜로 노출·호출
          03-langgraph-advanced : 서브그래프, 영속성(Sqlite), Store 장기기억, 병렬
Chapter4  10-harness      : deepagents + SKILL.md로 행동을 문서로 제어
          11-observability: Langfuse 트레이싱, @observe, 평가(score·LLM judge)
```

한 줄로 요약하면 이렇다.

> **호출(call)을 체인(chain)으로, 체인을 그래프(graph)로, 그래프를 시스템(system)으로.** 그리고 시스템이 되는 순간 필요한 것이 표준 프로토콜(MCP·A2A)과 관측성(Langfuse)이다.

### 실행 환경 공통 패턴

모든 파일이 같은 보일러플레이트로 시작한다.

```python
load_dotenv()
if not os.environ.get("GMS_KEY"):
    os.environ["GMS_KEY"] = os.environ.get("OPENAI_API_KEY", "")
if not os.environ.get("GMS_KEY"):
    os.environ["GMS_KEY"] = input("GMS_KEY를 입력하세요: ")

llm = ChatOpenAI(
    model=os.getenv('OPENAI_MODEL', 'gpt-5-nano'),
    api_key=os.environ["GMS_KEY"],
    base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/",
)
```

- **GMS**는 SSAFY가 제공하는 OpenAI API 프록시다. `base_url`만 프록시 주소로 바꾸면 OpenAI SDK·LangChain이 그대로 동작한다. 일반 환경이라면 `base_url` 인자를 빼고 `OPENAI_API_KEY`만 두면 된다.
- 기본 모델은 `gpt-5-nano`, 임베딩은 `text-embedding-3-small`.
- `.env.sample`에는 `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`, `GMS_KEY`, 그리고 Langfuse 키 3종(`LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST`)이 있다.

---

## LLM API 세 층위 (Chapter1/01-llm-api)

같은 질문("LLM이 무엇인지 3문장으로 설명해줘")을 세 가지 방법으로 호출한다. 아래로 갈수록 코드가 짧아지고, 대신 프레임워크가 해 주는 일이 늘어난다.

### 층위 1 — 순수 HTTP (`01_requests.py`)

```python
url = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1/responses'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
payload = {'model': model, 'input': 'LLM이 무엇인지 3문장으로 설명해줘.'}

response = requests.post(url, headers=headers, json=payload, timeout=30)
response.raise_for_status()
data = response.json()
```

- 엔드포인트가 `/v1/chat/completions`가 아니라 **`/v1/responses`** 다. 코드 주석에 따르면 Responses API는 Chat Completions의 후속 API로, `input` 필드 하나로 단순 문자열과 대화 내역을 모두 받는다.
- 인증 헤더(`Bearer`), 직렬화, 타임아웃, 에러 처리(`raise_for_status`)를 전부 직접 챙겨야 한다.

### 층위 2 — OpenAI SDK (`02_openai.py`)

```python
client = OpenAI(api_key=os.environ["GMS_KEY"],
                base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1/")

# Single Turn — 문자열을 주면 사용자 메시지로 처리
response = client.responses.create(model=model, input='LLM이 무엇인지 3문장으로 설명해줘.')
print(response.output_text)

# Multi Turn — role 있는 메시지 리스트로 맥락 유지
context = [
    {'role': 'developer', 'content': '너는 단답형 답변 챗봇이야. ...'},
    {'role': 'user', 'content': '대한민국의 수도는 어디지?'},
]
response_1 = client.responses.create(model=model, input=context)
context += response_1.output                          # 응답 자체를 맥락에 누적
context += [{'role': 'user', 'content': '그곳의 인구는 어느정도야?'}]
response_2 = client.responses.create(model=model, input=context)
```

- 역할이 `system`이 아니라 **`developer`** 인 것이 Responses API의 표기다.
- 멀티턴은 프레임워크가 아니라 **호출자가 `context` 리스트에 응답을 계속 이어 붙여서** 만든다. LLM API 자체는 무상태(stateless)라는 사실이 여기서 드러난다.
- 스트리밍은 `client.responses.stream(...)` 컨텍스트 매니저로 열고, 이벤트 타입 중 `output_text.delta`에 실제 텍스트 조각이 담긴다.

```python
with client.responses.stream(model=model, input='...') as stream:
    for event in stream:
        if 'output_text.delta' in event.type:
            print(event.delta, end='')
```

- `temperature`(0에 가까울수록 일관, 최대 2.0)와 `top_p`(상위 p% 토큰만) 설명이 주석으로 달려 있는데, **gpt-5 계열은 temperature를 지원하지 않아** 해당 호출부는 문자열 주석으로 막아 뒀다.

### 층위 3 — LangChain (`03_langchain.py`)

```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model=..., api_key=..., base_url=...)

messages = [
    SystemMessage(content='너는 초보자를 위한 AI 튜터야.'),
    HumanMessage(content='LLM이 무엇인지 3문장으로 설명해줘.'),
]
response = llm.invoke(messages)      # 단발 호출
for chunk in llm.stream(messages):   # 스트리밍
    print(chunk.content, end='', flush=True)
```

- 메시지가 dict가 아니라 **타입 있는 객체**(`SystemMessage` / `HumanMessage`)가 된다. 이 추상화 덕분에 뒤에서 모델 제공사를 바꿔도(OpenAI → Anthropic 등) 코드가 유지된다.
- `invoke` / `stream` 인터페이스는 다음 모듈에서 배우는 **Runnable 공통 규약**의 일부다. 즉 LLM 객체 자체가 이미 Runnable이다.

> **연결 고리** — 층위 1에서 직접 하던 일(직렬화·인증·에러 처리)을 층위 2가, 층위 2에서 직접 하던 일(맥락 누적, 프롬프트 조립)을 층위 3 이후의 체인·그래프가 맡는다. 추상화를 올라갈수록 "무엇을 위임했는지"를 알고 쓰는 것이 이 실습 전체의 태도다.

---

## LangChain 코어 — LCEL, 도구, 파서, 메모리 (Chapter1/02-langchain)

### LCEL과 Runnable (`01_lcel_runnable.py`)

**Runnable = `invoke`, `stream`, `batch`를 공통으로 제공하는 실행 단위.** LCEL(LangChain Expression Language)은 이 Runnable들을 `|` 연산자로 잇는 선언 방식이다.

```python
prompt = ChatPromptTemplate.from_messages([
    ('system', '너는 초보자를 위한 AI 튜터야.'),
    ('human', '{topic}을 초급자에게 3문장으로 설명해줘.'),
])
parser = StrOutputParser()

chain = prompt | llm | parser        # Runnable | Runnable → Runnable

answer = chain.invoke({'topic': 'LLM'})            # 단일 입력
for chunk in chain.stream({'topic': 'LangChain'}): # 청크 단위 출력
    ...
responses = chain.batch([{'topic': 'A'}, {'topic': 'B'}])  # 일괄 처리
```

- `prompt`, `llm`, `parser` 전부 Runnable 계열이고, **파이프 결과도 Runnable이므로 체인을 계속 이어 붙일 수 있다.**
- 체인 하나를 만들면 `invoke` / `stream` / `batch` 세 실행 방식이 공짜로 따라온다.

**RunnableParallel** — 여러 체인을 병렬 실행해 결과를 dict로 모은다.

```python
pros_chain = ChatPromptTemplate.from_template('{country}로 여행갈 때의 장점을 ...') | llm | StrOutputParser()
cons_chain = ChatPromptTemplate.from_template('{country}로 여행갈 때의 단점을 ...') | llm | StrOutputParser()

runnable = RunnableParallel(pros=pros_chain, cons=cons_chain)
answers = runnable.invoke({'country': '베트남'})   # {'pros': ..., 'cons': ...}
```

그리고 중요한 문법 설탕 — **일반 dict가 파이프 사이에 들어가면 자동으로 RunnableParallel처럼 동작한다.**

```python
parallel_dict = RunnablePassthrough() | {
    'pros': ChatPromptTemplate.from_template('...') | llm | StrOutputParser(),
    'cons': ChatPromptTemplate.from_template('...') | llm | StrOutputParser(),
}
```

**RunnablePassthrough** — 입력을 그대로 넘기면서 부가 필드를 얹는다.

```python
passthrough = RunnablePassthrough.assign(length=lambda x: get_question_length(x['question']))
passthrough.invoke({'question': 'RunnablePassthrough의 역할이 뭐야?'})
# → {'question': '...', 'length': 24}  (원본 유지 + 필드 추가)

chain = passthrough | prompt | llm | StrOutputParser()
```

**RunnableLambda** — 일반 파이썬 함수를 Runnable로 감싼다.

```python
acronym_dict = {'GPT': 'Generative Pre-trained Transformer', ...}
def translate_acronym(acronym: str):
    return acronym_dict.get(acronym, acronym)

chain = {'topic': RunnableLambda(translate_acronym)} | prompt | llm | StrOutputParser()
chain.invoke('GPT')   # 'GPT' → 'Generative Pre-trained Transformer' → 프롬프트 변수로
```

| 조합 도구 | 역할 | 전형적 쓰임 |
|---|---|---|
| `RunnableParallel` | 여러 체인 동시 실행, 결과 dict | 장점/단점 동시 생성, RAG의 context+question |
| `RunnablePassthrough` | 입력 통과(+`assign`으로 필드 추가) | 원본 질문을 보존한 채 부가정보 주입 |
| `RunnableLambda` | 함수를 체인 부품으로 | 전처리, 매핑, 포맷 변환 |

### 도구 호출 — 수동 루프 (`02_tool_calling.py`)

핵심 흐름: **사용자 질문 → LLM이 필요한 도구 결정 → 도구 실행 → 결과를 다시 LLM에 → 최종 답**.

```python
@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 조회한다."""
    fake_data = {'서울': '맑음, 기온 22°C', '부산': '흐림, 기온 24°C', '제주': '비, 기온 20°C'}
    return fake_data.get(city, f'{city}의 날씨 데이터를 찾을 수 없습니다.')

@tool
def calculate(expression: str) -> str:
    """수학 수식을 계산한다. 예: '2 + 3 * 4'"""
    try:
        result = eval(expression, {'__builtins__': {}})  # noqa: S307
        return str(result)
    except Exception as e:
        return f'계산 오류: {e}'

tools = [get_weather, calculate]
llm_with_tools = llm.bind_tools(tools)      # 호출마다 도구 스키마 자동 포함
tool_map = {t.name: t for t in tools}
```

- `@tool` 데코레이터: **docstring이 LLM에게 전달되는 도구 설명**이 되고, **타입 힌트가 JSON Schema로 변환**돼 파라미터 형식을 알린다. 설명을 대충 쓰면 LLM이 도구를 잘못 고른다.
- `bind_tools()`는 매 호출에 도구 스키마를 실어 보내는 래핑이다.

수동 루프의 뼈대:

```python
def run_with_tools(question: str) -> str:
    messages = [HumanMessage(content=question)]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:          # 도구 요청이 없으면 = 최종 답변
            return response.content
        for call in response.tool_calls:     # 있으면 전부 실행해서
            tool_fn = tool_map[call['name']]
            result = tool_fn.invoke(call['args'])
            messages.append(ToolMessage(     # 결과를 ToolMessage로 되돌려준다
                content=str(result),
                tool_call_id=call['id'],     # 어느 호출의 결과인지 매칭하는 id
            ))
```

- 반복 구조인 이유: "서울과 부산 날씨를 비교해줘" 같은 복합 질문은 도구를 여러 번 부른 뒤에야 최종 답이 나온다.
- `ToolMessage`의 `tool_call_id`가 요청-응답을 짝지어 준다. 빼먹으면 API 에러가 난다.
- 코드 주석: **"LangGraph의 ToolNode가 이 루프를 자동화한다"** → `Chapter2/04-langgraph/03_tool_node.py`로 이어진다.

### 구조화 출력 (`03_output_parser.py`)

LLM 출력(자유 텍스트)을 프로그램이 쓸 수 있는 구조(Pydantic 객체)로 받는 두 가지 방식.

```python
class MovieReview(BaseModel):
    title: str = Field(description='영화 제목')
    genre: str = Field(description='장르 (예: 액션, 드라마, SF)')
    rating: float = Field(description='평점 (1.0 ~ 10.0)')
    summary: str = Field(description='100자 이내 한 줄 요약')
    recommend: bool = Field(description='추천 여부')
```

**방법 1 — PydanticOutputParser**: 프롬프트에 JSON 형식 지시문을 주입해 유도.

```python
parser = PydanticOutputParser(pydantic_object=MovieReview)
prompt = ChatPromptTemplate.from_messages([
    ('system', '영화 리뷰 전문가야. 다음 형식으로 응답해.\n{format_instructions}'),
    ('human', '{movie} 리뷰 작성해줘'),
]).partial(format_instructions=parser.get_format_instructions())

chain1 = prompt | llm | parser          # LLM이 지시를 안 따르면 파싱 실패 가능
```

**방법 2 — with_structured_output() (권장)**: LLM의 function-calling 기능을 이용해 형식을 강제.

```python
structured_llm = llm.with_structured_output(MovieReview)
chain2 = prompt2 | structured_llm       # 프롬프트에 형식 지시 불필요
review: MovieReview = chain2.invoke({'movie': '기생충'})
```

| | PydanticOutputParser | with_structured_output() |
|---|---|---|
| 안정성 | LLM의 지시 이행에 의존 | function-calling으로 보장 |
| 프롬프트 | `format_instructions` 주입 필요 | 단순 |
| 모델 요구 | 모든 텍스트 LLM 가능 | function-calling 지원 필요 |
| 권장 | 구형 모델·커스텀 파싱 | 최신 모델 기본 권장 |

- 뒤에서 재등장한다: Supervisor의 라우팅 결정(`RouteDecision`), RAG 평가의 채점표(`EvalScore`) 모두 `with_structured_output` 기반이다. **"LLM의 판단을 코드의 분기·수치로 쓰고 싶을 때"의 표준 수법.**

### 메모리 전략 1 — RunnableWithMessageHistory (`04_memory_runnable.py`)

대화 기록을 **체인 바깥**의 세션 저장소에서 관리하고, wrapper가 실행 시점에 주입한다.

```python
session_store: dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ('system', '너는 친절한 AI 어시스턴트야.'),
    MessagesPlaceholder(variable_name='history'),   # 이전 대화가 여기 삽입
    ('human', '{input}'),
])
chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(
    chain, get_session_history,
    input_messages_key='input', history_messages_key='history',
)

config_a = {'configurable': {'session_id': 'session_A'}}
chain_with_history.invoke({'input': '내 이름은 홍길동이야.'}, config=config_a)
chain_with_history.invoke({'input': '내 이름이 뭐야?'}, config=config_a)   # 기억함
# session_B로 부르면 A의 대화를 모른다 (세션 격리)
```

코드가 직접 명시한 한계:

- 히스토리가 체인 외부에 있어 **그래프와 통합이 어렵다**
- **도구 실행 결과가 메시지 흐름에 자동 포함되지 않는다**
- 분기·반복 구조에서 히스토리 관리가 번거롭다

### 메모리 전략 2 — LangGraph State (`05_memory_langgraph.py`)

대화 기록을 **State의 일부**로 넣고, checkpointer가 스레드별로 영속화한다.

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]   # reducer: 덮어쓰기가 아니라 누적(append)

def chatbot(state: State) -> dict:
    system = SystemMessage(content='너는 친절한 AI 어시스턴트야.')
    return {'messages': [llm.invoke([system] + state['messages'])]}

builder = StateGraph(State)
builder.add_node('chatbot', chatbot)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)

app = builder.compile(checkpointer=MemorySaver())   # 스레드별 State 유지

config_a = {'configurable': {'thread_id': 'thread_A'}}
app.invoke({'messages': [HumanMessage(content='내 이름은 홍길동이야.')]}, config=config_a)
app.invoke({'messages': [HumanMessage(content='내 이름이 뭐야?')]}, config=config_a)  # 기억함
```

- `add_messages` reducer가 "노드가 반환한 messages를 기존 리스트에 **append**"로 병합해 준다. reducer가 없으면 필드는 덮어쓰기다.
- `app.get_state(config)`로 스냅샷을 꺼내 볼 수 있다. `snapshot.next`가 `()`이면 실행 완료 상태.

두 전략 비교 (코드의 표를 재구성):

| | LangChain (RunnableWithMessageHistory) | LangGraph (MemorySaver) |
|---|---|---|
| 히스토리 위치 | 체인 외부 (session_store) | State 내부 (messages 필드) |
| 도구 결과 통합 | 수동 처리 필요 | 자동 (ToolMessage로 축적) |
| 분기/반복 | 구현 복잡 | 그래프 구조로 자연스럽게 표현 |
| 영속성 | 별도 저장소 연결 필요 | checkpointer 교체만으로 전환 |
| 권장 시나리오 | 단순 Q&A 챗봇 | Agent, 복잡한 대화 흐름 |

> **연결 고리** — 세션 격리 키가 전략 1은 `session_id`, 전략 2는 `thread_id`다. 이름만 다르고 발상은 같다. 전략 2의 checkpointer는 뒤의 HITL(중단·재개), 영속성(SqliteSaver), Time-Travel의 기반 시설이 된다.

---

## RAG 파이프라인 (Chapter1/03-rag + Chapter2/06-rag-streamlit)

실습 데이터는 `data/meritz_pet_insurance.pdf`(메리츠 펫보험 약관, 약 2MB). "약관 PDF에 대해 질문하면 근거 문단을 찾아 답하는" 파이프라인을 4개 파일로 단계별 구축한다.

### 1단계 — 문서 로딩과 청킹 (`01_data_loading.py`)

```python
loader = PDFMinerLoader(str(PDF_PATH.resolve()))
documents = loader.load()                  # list[Document] — page_content + metadata

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 작을수록 검색 단위가 정밀, 대신 문맥이 줄어든다
    chunk_overlap=75,    # 클수록 문맥 연결성↑, 대신 중복·비용↑
)
chunks = text_splitter.split_documents(documents)
```

- **Document** = LangChain이 본문(`page_content`)과 메타데이터(`metadata`)를 다루는 기본 단위.
- **청킹이 필요한 이유**: 문서 전체를 LLM에 넣기 어렵고, 검색 단위가 커지면 관련 없는 내용이 딸려 온다.
- `RecursiveCharacterTextSplitter`는 문단 → 줄 → 단어 → 문자 순서로 분할 지점을 찾는다 (자연스러운 경계 우선).
- `chunk_size` / `chunk_overlap`은 **검색 정확도와 문맥 보존 사이의 트레이드오프 손잡이**다.

### 2단계 — 임베딩과 유사도 (`02_embeddings.py`)

```python
embeddings = OpenAIEmbeddings(model='text-embedding-3-small', api_key=..., base_url=...)

sentences = ['강아지가 공원에서 뛰어놀고 있다.', '개가 잔디밭에서 달리고 있다.', '오늘 주식시장이 크게 하락했다.']
vectors = embeddings.embed_documents(sentences)   # 텍스트 리스트 → 벡터 리스트

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# [강아지] vs [개]   : 높게 나와야 함
# [강아지] vs [주식] : 낮게 나와야 함

query_vec = np.array(embeddings.embed_query('애완동물이 뛰노는 모습'))  # 질문 1건용
```

- 임베딩 = **텍스트의 의미를 숫자 벡터로**. 의미가 비슷하면 벡터 공간에서 가깝다.
- RAG의 "관련 문서 검색"의 실체는 **이 벡터 거리(코사인 유사도) 계산**이다.
- API가 둘로 나뉜 것 주의: 문서 색인용 `embed_documents(list)` vs 질의용 `embed_query(str)`.

### 3단계 — 벡터스토어와 리트리버 (`03_vector_store.py`)

```python
vectorstore = Chroma.from_documents(
    chunks, embedding=embeddings,
    # persist_directory=str(...)  ← 디스크에 저장하고 싶을 때
)
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})   # 상위 3개 청크 반환

results = retriever.invoke(question)    # retriever도 Runnable — invoke로 검색
```

- 2단계의 "모든 벡터와 일일이 코사인 유사도 계산"을 **Chroma**(벡터 DB)가 대신한다. 색인·저장·최근접 검색이 한 번에.
- `as_retriever()`로 감싸면 **검색기 자체가 Runnable**이 되어 LCEL 체인에 바로 꽂힌다.
- `persist_directory`를 주지 않으면 인메모리 — 프로세스가 끝나면 색인도 사라진다 (실습이라 매번 재색인).

### 4단계 — RAG 체인 조립 (`04_langchain_rag.py`)

```python
prompt = ChatPromptTemplate.from_messages([
    ('system', '당신은 문서 기반 QA 어시스턴트입니다. 주어진 context만 근거로 답하세요.'),
    ('human', 'context:\n{context}\n\nquestion:\n{question}'),
])

def format_docs(docs):
    return '\n\n'.join(doc.page_content for doc in docs)

rag_chain = (
    {'context': retriever | format_docs, 'question': RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for message in rag_chain.stream(question):   # 스트리밍으로 답변 출력
    print(message, end='')
```

- 첫 단이 **dict → 자동 RunnableParallel**: 사용자 질문 하나가 두 갈래로 흐른다. `context` 갈래는 `retriever | format_docs`(검색→문자열 합치기), `question` 갈래는 `RunnablePassthrough()`(그대로 통과).
- 시스템 프롬프트의 "**주어진 context만 근거로 답하세요**"가 환각 억제 장치다.
- LCEL 모듈에서 배운 부품(dict 병렬, Passthrough, 파서)이 전부 재사용된다 — RAG 체인은 새 개념이 아니라 **조립**이다.

### UI 붙이기 — Streamlit 챗봇 (`Chapter2/06-rag-streamlit/app.py`)

```python
@st.cache_resource          # 앱 재실행마다 재색인하지 않도록 리소스 캐시
def load_rag_chain():
    ...                     # 로딩→청킹→임베딩→Chroma→retriever→체인 (4단계와 동일)
    return chain

if 'messages' not in st.session_state:
    st.session_state.messages = []          # 대화 기록 (새로고침 전까지)

if prompt := st.chat_input('질문을 입력하세요 (예: 보험료는 어떻게 계산되나요?)'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('assistant'):
        rag_chain = load_rag_chain()
        response = st.write_stream(rag_chain.stream(prompt))   # 체인 스트림을 그대로 UI로
    st.session_state.messages.append({'role': 'assistant', 'content': response})
```

- `@st.cache_resource`가 없으면 **질문할 때마다 PDF 로딩·임베딩을 다시 한다** (비용 폭탄).
- `st.write_stream(chain.stream(...))` — LCEL의 스트리밍 인터페이스가 UI 스트리밍과 그대로 연결된다.
- 이 챗봇의 대화 기록은 `st.session_state`(UI 레벨)에만 있고 **체인에는 주입되지 않는다**. 즉 이전 질문을 기억하는 멀티턴 RAG가 아니다 — 메모리 전략(04·05)과 결합하는 것이 다음 단계 과제.

> **연결 고리** — RAG 5단계: `PDFMinerLoader`(로딩) → `RecursiveCharacterTextSplitter`(청킹) → `OpenAIEmbeddings`(임베딩) → `Chroma`(색인·검색) → LCEL 체인(생성). 검색은 임베딩 유사도, 생성은 "context만 근거로" 프롬프트. 이 구조의 품질 평가는 Chapter4의 `05_rag_evaluation_extra.py`에서 다시 만난다.

---

## LangGraph 기초 — 그래프로 만드는 에이전트 (Chapter2/04-langgraph)

### 3대 요소 — State, Node, Edge (`01_basic_graph.py`)

```python
# 1. State: 그래프 전체에서 공유되는 데이터 구조 (TypedDict 또는 Pydantic)
class State(TypedDict):
    messages: Annotated[list, add_messages]   # add_messages reducer → 누적(append)

# 2. Node: State를 받아 "State의 일부(dict)"를 반환하는 함수
def chatbot_node(state: State) -> dict:
    response = llm.invoke(state['messages'])
    return {'messages': [response]}           # 반환 dict는 reducer 규칙으로 병합

# 3. Edge: 노드 간 흐름. START/END는 LangGraph 제공 진입·종료 지점
builder = StateGraph(State)
builder.add_node('chatbot', chatbot_node)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)
app = builder.compile()

print(app.get_graph().draw_mermaid())   # 그래프 구조를 Mermaid 다이어그램으로 출력
```

- 노드는 **전체 State가 아니라 바뀐 부분만** 반환한다. 병합 방법은 각 필드의 reducer가 정한다 (`add_messages`면 누적, 없으면 덮어쓰기).
- `draw_mermaid()`로 그래프를 시각화해 구조를 검증할 수 있다 — 그래프가 커질수록 유용.

### 조건부 엣지 (`02_conditional_edge.py`)

언어를 감지해 한국어/영어 응답 노드로 분기하는 예제.

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    language: str            # 감지된 언어 ('ko' | 'en') — messages 외의 상태 필드

def detect_language(state: State) -> dict:
    last = state['messages'][-1].content
    result = llm.invoke(f"다음 텍스트의 언어를 'ko' 또는 'en' 중 하나로만 답해: {last}")
    lang = 'ko' if 'ko' in result.content.lower() else 'en'
    return {'language': lang}

# 라우팅 함수: State를 받아 다음 노드 이름을 반환
def route_by_language(state: State) -> Literal['korean_response', 'english_response']:
    return 'korean_response' if state.get('language') == 'ko' else 'english_response'

builder.add_edge(START, 'detect_language')
builder.add_conditional_edges('detect_language', route_by_language)   # 분기 지점
builder.add_edge('korean_response', END)
builder.add_edge('english_response', END)
```

- 분기 로직이 if문으로 노드 안에 숨지 않고 **그래프 위상(topology)으로 드러난다**는 것이 그래프 방식의 장점.
- LLM에게 분류를 시키고(`'ko' 또는 'en' 중 하나로만 답해`) 그 결과를 코드 분기에 쓰는 패턴 — 뒤의 Supervisor에서 structured output으로 더 견고해진다.

### ToolNode와 ReAct 루프 (`03_tool_node.py`)

`02_tool_calling.py`의 수동 while 루프를 그래프가 대체한다.

```python
@tool
def get_exchange_rate(base_currency: str, target_currency: str) -> float:
    """고정 환율을 반환한다. base_currency와 target_currency는 USD, KRW, EUR 중 하나."""
    rates = {('USD', 'KRW'): 1350.0, ('KRW', 'USD'): 1 / 1350.0, ...}
    if base_currency == target_currency:
        return 1.0
    return rates.get((base_currency, target_currency), -1.0)

@tool
def calculate(expression: str) -> float:
    """간단한 수식을 계산한다. 예: '1350 * 100'"""
    allowed = set('0123456789+-*/(). ')
    if not all(c in allowed for c in expression):
        raise ValueError('허용되지 않는 문자가 포함되어 있습니다.')
    return eval(expression)  # noqa: S307

tools = [get_exchange_rate, calculate]
llm = ChatOpenAI(...).bind_tools(tools)

def agent_node(state: State) -> dict:
    return {'messages': [llm.invoke(state['messages'])]}

tool_node = ToolNode(tools)   # tool_calls 파싱 → 도구 실행 → ToolMessage 반환

builder.add_node('agent', agent_node)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'agent')
builder.add_conditional_edges('agent', tools_condition)  # tool_calls 있으면 'tools', 없으면 END
builder.add_edge('tools', 'agent')                       # 도구 실행 후 다시 agent → ReAct 루프
```

- **ToolNode**: AI 메시지의 `tool_calls`를 파싱해 해당 도구를 실행하고 결과를 `ToolMessage` 리스트로 반환 — 수동 루프의 for문 부분.
- **tools_condition**: 마지막 메시지에 `tool_calls`가 있으면 `'tools'`로, 없으면 END로 라우팅 — 수동 루프의 if문 부분.
- `tools → agent` 엣지가 루프를 닫아 **에이전트가 도구 결과를 보고 다시 판단**하게 만든다. 이 순환 구조가 ReAct 패턴이다.

**create_agent** — 위 그래프를 한 줄로 생성하는 편의 함수.

```python
from langchain.agents import create_agent
agent = create_agent(llm, tools)
result = agent.invoke({'messages': [HumanMessage(content='50유로는 몇 원이야?')]})
```

- 코드 주석 기준: 커스텀 노드·엣지가 필요 없을 때 사용하고, 내부적으로 같은 그래프를 자동 생성한다. **멀티에이전트처럼 여러 에이전트가 통신하는 구조는 StateGraph 직접 조립이 필요하다.**

### Human-in-the-Loop — 승인·거부 (`04_human_in_the_loop.py`)

이메일 전송처럼 **부수효과가 있는 도구**는 실행 전에 사람이 확인해야 한다.

```python
app = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=['tools'],    # tools 노드 실행 "직전"에 그래프 일시 중단
)
config = {'configurable': {'thread_id': 'hitl_demo'}}

# 1단계: tools 직전까지 실행하고 멈춘다
app.invoke({'messages': [HumanMessage(content='kim@example.com에게 ... 이메일을 보내줘.')]}, config=config)

state = app.get_state(config)
pending_tools = state.values['messages'][-1].tool_calls   # 대기 중인 도구 호출 확인

# 2단계(승인): None을 입력하면 중단 지점부터 이어서 실행
result = app.invoke(None, config=config)
```

거부는 한 수 더 얹는다 — **그래프를 속여서 "도구가 거부 응답을 반환한 것처럼"** 상태를 조작한다.

```python
rejected_calls = state2.values['messages'][-1].tool_calls
rejection_messages = [
    ToolMessage(content='사용자가 이메일 전송을 취소했습니다.', tool_call_id=tc['id'])
    for tc in rejected_calls
]
app.update_state(config2, {'messages': rejection_messages}, as_node='tools')  # tools가 실행된 셈 치기
result2 = app.invoke(None, config=config2)   # agent가 취소 사실을 보고 마무리 답변
```

- 이 모든 것의 전제가 **checkpointer**다. 중단 시점의 State가 저장돼 있어야 나중에 이어서 실행할 수 있다.
- `invoke(None, config)` = "새 입력 없이, 저장된 지점부터 재개".
- `as_node='tools'` = "이 상태 갱신을 tools 노드가 한 것으로 기록" → 다음 실행 노드가 자연스럽게 agent가 된다.

### HITL 대화형 버전 (`05_hitl_interactive.py`)

같은 구조를 y/n/q 입력 루프로 감싼 실전형. 거부 시 사유까지 전달한다.

```python
def reject_tool_calls(config, tool_calls, reason: str) -> None:
    rejection_messages = [
        ToolMessage(content=f'사용자가 도구 실행을 거부했습니다. 사유: {reason}',
                    tool_call_id=tool_call['id'])
        for tool_call in tool_calls
    ]
    app.update_state(config, {'messages': rejection_messages}, as_node='tools')

# 루프: 대기 중 tool_calls 표시 → y(승인·재개) / n(사유 입력 후 거부·재개) / q(종료)
```

- 거부 사유가 `ToolMessage` 내용으로 들어가므로, **에이전트가 사유를 읽고 대안을 제시**할 수 있다 ("다른 제목으로 보낼까요?" 등).

---

## 멀티에이전트 패턴 (Chapter2/05-multi-agent)

### 패턴 1 — 고정 파이프라인: Researcher → Writer (`01_researcher_writer.py`)

역할이 다른 두 에이전트가 **정해진 순서**로 일한다. State에 역할별 결과 필드를 둔다.

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    research_result: str    # Researcher가 수집한 정보
    draft: str              # Writer가 작성한 초안

# Researcher: search_web 도구를 쓰는 에이전트 (도구 호출 루프 포함)
def researcher_node(state: State) -> dict:
    system = SystemMessage(content='너는 전문 리서처야. search_web 도구를 사용해 ... 조사하고 ...')
    response = researcher_llm.invoke([system] + state['messages'])
    return {'messages': [response]}

def researcher_tools_node(state: State) -> dict:
    tool_result = researcher_tool_node.invoke(state)      # ToolNode 실행
    last_tool_msg = tool_result['messages'][-1]
    return {'messages': tool_result['messages'],
            'research_result': last_tool_msg.content}     # 도구 결과를 State 필드에 저장

def researcher_condition(state: State):
    last = state['messages'][-1]
    if hasattr(last, 'tool_calls') and last.tool_calls:
        return 'researcher_tools'
    return 'writer'                                       # 조사가 끝나면 Writer로

# Writer: 리서치 결과를 컨텍스트로 받아 글 작성
def writer_node(state: State) -> dict:
    system = SystemMessage(content='너는 전문 작가야. ... 서론, 본론, 결론 구조를 갖춰줘.')
    context = f'[리서치 결과]\n{state.get("research_result", "")}'
    response = llm.invoke([system, HumanMessage(content=context), *state['messages']])
    return {'messages': [response], 'draft': response.content}

builder.add_edge(START, 'researcher')
builder.add_conditional_edges('researcher', researcher_condition)
builder.add_edge('researcher_tools', 'researcher')   # 도구 후 다시 researcher (ReAct)
builder.add_edge('writer', END)
```

- `search_web`은 데모용 고정 문자열 반환. 실제로는 Tavily·SerpAPI 등을 쓴다고 주석에 명시.
- ReAct 루프(researcher ↔ researcher_tools)가 **한 에이전트의 내부 구조**로 들어가고, 그 바깥에 에이전트 간 흐름(researcher → writer)이 있다 — 그래프 안의 그래프 같은 2단 구조.
- **에이전트 간 통신 채널이 State 필드**(`research_result`)다. 메시지 히스토리에 섞지 않고 구조화된 필드로 넘긴다.

### 패턴 2 — Supervisor 라우팅 (`02_supervisor.py`)

순서를 코드에 고정하지 않고 **Supervisor LLM이 매 턴 다음 작업자를 결정**한다.

```python
class RouteDecision(BaseModel):
    next: Literal['researcher', 'writer', 'FINISH']
    reason: str

supervisor_llm = llm.with_structured_output(RouteDecision)   # 라우팅 결정을 구조화 출력으로

SUPERVISOR_PROMPT = """너는 멀티 에이전트 시스템의 Supervisor야.
다음 에이전트 중 하나를 선택해 작업을 지시하거나 완료를 선언해줘.
- researcher: 웹 검색으로 정보를 수집해야 할 때
- writer: 수집된 정보를 바탕으로 글을 작성해야 할 때
- FINISH: 모든 작업이 완료됐을 때
현재 상황:
- 리서치 완료 여부: {research_done}
- 초안 작성 여부: {draft_done}
"""

def supervisor_node(state: State) -> dict:
    prompt = SUPERVISOR_PROMPT.format(
        research_done='완료' if state.get('research_result') else '미완료',
        draft_done='완료' if state.get('draft') else '미완료',
    )
    decision = supervisor_llm.invoke([SystemMessage(content=prompt), *state['messages']])
    return {'next': decision.next,
            'messages': [SystemMessage(content=f'[Supervisor → {decision.next}] {decision.reason}')]}

def route(state: State) -> Literal['researcher', 'writer', '__end__']:
    return state['next'] if state['next'] != 'FINISH' else END

builder.add_edge(START, 'supervisor')
builder.add_conditional_edges('supervisor', route)
builder.add_edge('researcher', 'supervisor')    # 작업자는 끝나면 Supervisor에게 보고
builder.add_edge('writer', 'supervisor')
```

- 허브 앤 스포크: **모든 작업자가 일을 마치면 Supervisor로 돌아온다.** 다음 단계 결정권이 항상 중앙에 있다.
- 라우팅 결정에 `with_structured_output(RouteDecision)`을 써서 **"researcher/writer/FINISH 중 하나"를 타입으로 강제** — 자유 텍스트 파싱보다 훨씬 견고하다.
- 프롬프트에 진행 상황(리서치/초안 완료 여부)을 **State에서 계산해 주입** — Supervisor가 상태를 보고 판단하게 만든다.
- 에이전트들의 활동 로그를 `SystemMessage`로 messages에 남긴다 (`[Researcher 완료] ...`) — 사람이 의사결정 흐름을 추적할 수 있다.

| | 파이프라인 (researcher_writer) | Supervisor |
|---|---|---|
| 흐름 결정 | 그래프에 고정 (엣지가 순서) | 매 턴 LLM이 결정 |
| 유연성 | 낮음 — 순서 바꾸려면 그래프 수정 | 높음 — 재조사·재작성 지시 가능 |
| 예측 가능성·비용 | 높음·저렴 (LLM 호출 최소) | 낮음·비쌈 (라우팅마다 LLM 호출) |
| 적합한 일 | 절차가 명확한 정형 업무 | 진행 상황에 따라 다음 일이 달라지는 업무 |

---

## 에이전트 생태계 표준 1 — MCP (Chapter3/01-mcp)

### MCP 서버 만들기 (`01_mcp_server.py`)

**MCP(Model Context Protocol)**: LLM 애플리케이션(호스트)과 외부 기능(도구·데이터) 사이의 표준 프로토콜. FastMCP는 MCP SDK 위의 고수준 래퍼로, 데코레이터 3종으로 서버를 정의한다.

```python
from fastmcp import FastMCP
mcp = FastMCP('AI 강의 튜토리얼 서버')

# ── Tool: LLM이 호출할 수 있는 함수
@mcp.tool()
def get_current_time() -> str:
    """현재 날짜와 시간을 반환한다."""
    return datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')

@mcp.tool()
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """체중(kg)과 키(cm)로 BMI를 계산한다."""
    ...  # BMI 계산 + 저체중/정상/과체중/비만 분류

# 할 일 관리 3종: add_task / list_tasks / complete_task (서버 메모리 _tasks 리스트 공유)

# ── Resource: LLM에게 제공할 데이터/문서 (URI로 식별)
@mcp.resource('config://app-info')
def get_app_info() -> str:
    """이 MCP 서버의 기본 정보를 제공한다."""
    return "서버명: ... 버전: 1.0.0 기능: ..."

# ── Prompt: 자주 쓰는 프롬프트 템플릿
@mcp.prompt()
def task_summary_prompt(user_name: str) -> str:
    """할 일 목록 요약 요청 프롬프트를 생성한다."""
    return f'{user_name}님의 할 일 목록을 우선순위별로 정리하고 ...'
```

실행 모드가 둘이다.

```python
if '--stdio' in sys.argv:
    mcp.run(transport='stdio', show_banner=False)   # MCP Host(Claude Code 등)와 직접 연결
else:
    mcp.run(transport='sse', host='0.0.0.0', port=8000)   # HTTP/SSE — localhost:8000/sse
```

- **stdio**: 호스트 프로세스가 서버를 자식 프로세스로 띄우고 표준입출력으로 통신. `show_banner=False`가 중요 — stdio에서 배너 출력이 섞이면 프로토콜 통신을 방해한다는 주석이 달려 있다.
- **SSE**: HTTP 기반. 다른 프로세스·다른 머신에서 URL로 접속.
- Claude Code 등록 명령까지 주석에 있다: `claude mcp add tutorial-server -- python /절대경로/01_mcp_server.py --stdio`

### MCP 클라이언트 + LangGraph (`02_mcp_client.py`)

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_CONFIG = {
    'tutorial': {
        "transport": "stdio",
        "command": sys.executable,                      # 현재 파이썬 인터프리터로
        "args": [str(BASE_DIR / "01_mcp_server.py"), '--stdio'],   # 서버를 직접 띄움
    },
    # SSE 모드로 연결할 때: {'transport': 'sse', 'url': 'http://localhost:8000/sse'}
}

async def main():
    client = MultiServerMCPClient(MCP_CONFIG)
    tools = await client.get_tools()        # 서버(들)에 연결해 도구 목록 수집

    llm = ChatOpenAI(...).bind_tools(tools) # MCP 도구를 여느 LangChain 도구처럼 바인딩
    tool_node = ToolNode(tools)
    # ... agent ↔ tools ReAct 그래프 (03_tool_node.py와 동일 구조)
    result = await app.ainvoke({'messages': [HumanMessage(content='지금 몇 시야?')]})
```

- `MultiServerMCPClient`는 이름 그대로 **서버 여러 개**를 한 설정으로 묶을 수 있다.
- `get_tools()`가 MCP 도구를 **LangChain Tool 인터페이스로 변환**해 주므로, `bind_tools`·`ToolNode`에 그대로 꽂힌다. 그래프 코드는 로컬 도구 때와 한 글자도 다르지 않다.
- 전부 `async`(`ainvoke`)로 돌아간다 — MCP 통신이 비동기 IO이기 때문.

> **연결 고리** — `@tool`(로컬 함수) → MCP 도구(프로세스 밖, 표준 프로토콜)로 바뀌어도 에이전트 그래프는 불변. **도구의 출처를 표준화하면 에이전트와 도구 생태계가 분리된다**는 것이 MCP의 핵심 가치다.

---

## 에이전트 생태계 표준 2 — A2A (Chapter3/02-a2a)

### A2A 서버 — 에이전트를 프로토콜로 노출 (`01_a2a_server.py`)

**A2A(Agent-to-Agent)**: Google이 제안한 에이전트 간 통신 표준. 에이전트를 HTTP 서비스로 노출하면 프레임워크(LangGraph, CrewAI, AutoGen 등)와 무관하게 서로 통신할 수 있다.

내부는 평범한 LangGraph ReAct 에이전트(search_web 도구)이고, 그 둘레에 A2A 계층을 세 조각으로 감싼다.

**(1) AgentExecutor — 요청을 받아 에이전트를 실행하고 결과를 발행**

```python
import a2a.types as t
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

class ResearcherExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input() or ''    # 사용자 메시지의 텍스트 파트 수집
        result = await langgraph_agent.ainvoke({'messages': [HumanMessage(content=user_text)]})
        answer = result['messages'][-1].content
        await event_queue.enqueue_event(
            t.Message(
                role=t.Role.ROLE_AGENT,
                parts=[t.Part(text=answer)],
                message_id=str(uuid.uuid4()),
                task_id=context.task_id,
                context_id=context.context_id,
            )
        )
```

- 코드 주석: **a2a-sdk 1.x는 Pydantic 대신 protobuf 타입(`a2a.types`)을 쓴다.** protobuf는 `.proto` 스키마에서 언어별 코드를 생성하는 직렬화 포맷 — gRPC 기반 크로스 플랫폼 통신을 위해 SDK가 전환됐다. (1.x에서는 `TextPart` 대신 `t.Part(text=...)`를 직접 쓴다.)

**(2) Agent Card — 에이전트의 명함(발견 메커니즘)**

```python
agent_card = t.AgentCard(
    name='Researcher Agent',
    description='주어진 주제를 웹에서 조사하고 요약 정보를 제공합니다.',
    version='1.0.0',
    default_input_modes=['text'], default_output_modes=['text'],
    capabilities=t.AgentCapabilities(streaming=False),
    supported_interfaces=[t.AgentInterface(url='http://localhost:8001')],
    skills=[t.AgentSkill(id='web_research', name='웹 리서치',
                         description='주제를 검색해 핵심 정보를 수집하고 정리합니다.',
                         tags=['research', 'web'],
                         examples=['AI Agent 기술 트렌드 조사', ...])],
)
```

- 클라이언트는 `/.well-known/agent-card.json`에서 이 카드를 읽어 에이전트를 **발견(discover)** 한다 — "무엇을 할 수 있는 에이전트인지"의 기계가 읽는 소개서.

**(3) Starlette 앱 조립 — 라우트 2종**

```python
request_handler = DefaultRequestHandlerV2(
    agent_executor=ResearcherExecutor(),
    task_store=InMemoryTaskStore(),          # Task 상태 저장
    agent_card=agent_card,
    queue_manager=InMemoryQueueManager(),
)
routes = [
    *create_agent_card_routes(agent_card),           # /.well-known/agent-card.json
    *create_jsonrpc_routes(request_handler, rpc_url='/'),   # JSON-RPC 엔드포인트
]
app = Starlette(routes=routes)
uvicorn.run(app, host='0.0.0.0', port=8001)
```

### A2A 클라이언트 — Task 생성과 폴링 (`02_a2a_client.py`)

```python
async def jsonrpc(http, method: str, params: dict) -> dict:
    payload = {'jsonrpc': '2.0', 'id': str(uuid.uuid4()), 'method': method, 'params': params}
    response = await http.post(f'{RESEARCHER_URL}/', json=payload)
    ...

# 요청 생성
await jsonrpc(http, 'SendMessage', {
    'message': {'role': 'ROLE_USER', 'parts': [{'text': query}], 'messageId': str(uuid.uuid4())},
})

# 상태 조회 (완료까지 1초 간격 폴링, 최대 30회)
task = await jsonrpc(http, 'GetTask', {'id': task_id, 'historyLength': 10})
```

- 헤더에 프로토콜 버전을 싣는다: `{VERSION_HEADER: PROTOCOL_VERSION_1_0}`.
- **A2A v1에서는 `SendMessage`가 Task 대신 Message를 즉시 반환할 수 있다** — 코드가 두 경로를 모두 처리한다: 즉시 응답이면 그대로 반환, Task 모드면 종료 상태(`completed`/`failed`/`canceled` 등)까지 폴링.
- 응답 파싱이 유난히 방어적이다 — `get_nested()`로 camelCase/snake_case 혼재를 흡수하고, task id 후보를 6군데서 찾고, 결과 텍스트를 artifacts → status.message → history 순으로 뒤진다. **스펙 전환기(1.x) 구현체들의 편차를 흡수하는 현실적 코드.**

흐름 전체:

```text
[클라이언트]                                  [Researcher A2A 서버 :8001]
GET /.well-known/agent-card.json  ───────▶   Agent Card 반환 (발견)
JSON-RPC SendMessage(질문)        ───────▶   AgentExecutor.execute()
                                              └─ 내부 LangGraph 에이전트 실행
Message 즉시 응답 ◀── 또는 ──▶ Task 생성
JSON-RPC GetTask(task_id) 폴링    ───────▶   상태/결과 반환 (completed까지)
이후: Writer(로컬 LLM)가 리서치 결과로 글 작성   ← 이종 에이전트 간 역할 분리
```

### MCP vs A2A — 무엇의 표준인가

| | MCP | A2A |
|---|---|---|
| 연결 대상 | LLM 앱(호스트) ↔ **도구·데이터** | **에이전트** ↔ **에이전트** |
| 노출 단위 | tool / resource / prompt | Agent Card + skills |
| 발견 | 호스트 설정에 서버 등록 | `/.well-known/agent-card.json` |
| 통신 | stdio / SSE(HTTP) | HTTP + JSON-RPC (protobuf 타입) |
| 이 실습의 예 | 시간·BMI·할일 도구 서버 | Researcher 에이전트 서비스 |

> **연결 고리** — Chapter2의 멀티에이전트는 **한 프로세스 안 한 그래프**의 협업이고, A2A는 **프로세스·프레임워크·조직 경계를 넘는** 협업이다. Supervisor가 부르던 researcher_node가 A2A에서는 네트워크 건너편의 서비스가 된 것.

---

## LangGraph 고급 (Chapter3/03-langgraph-advanced)

### 서브그래프 (`01_subgraph.py`)

독립적으로 컴파일한 그래프를 부모 그래프의 노드로 쓴다. 복잡한 워크플로우를 **재사용 가능한 단위**로 분리하는 수단.

```python
# 서브그래프 전용 State — 부모 State와 완전히 독립
class SummaryState(TypedDict):
    text: str
    summary: str

summary_builder = StateGraph(SummaryState)
summary_builder.add_node('summarize', summarize_node)   # 한 문장 요약
summary_builder.add_node('translate', translate_node)   # 영어로 번역
summary_builder.add_edge(START, 'summarize')
summary_builder.add_edge('summarize', 'translate')
summary_builder.add_edge('translate', END)
summary_subgraph = summary_builder.compile()            # 독립 컴파일

# 부모 그래프의 노드 안에서 서브그래프를 "함수처럼" 호출
class ParentState(TypedDict):
    messages: Annotated[list, add_messages]
    document: str
    summary: str

def summarize_document(state: ParentState) -> dict:
    result = summary_subgraph.invoke({'text': state['document'], 'summary': ''})
    return {'summary': result['summary']}    # 부모 State 필드로 결과 매핑

# 부모: fetch_document → summarize_document(서브그래프) → respond
```

- 이 예제의 방식은 **노드 함수 안에서 서브그래프를 invoke하고 State를 수동 매핑**하는 것. State 스키마가 달라도 노드 함수가 어댑터 역할을 하므로 문제없다.
- 요약·번역 파이프라인을 다른 그래프에서도 재사용할 수 있게 된다 — 함수 추출(refactoring)의 그래프 버전.

### 영속성 — 체크포인터 3단계와 Time-Travel (`02_persistence.py`)

```python
# MemorySaver  : 프로세스 메모리 → 재시작하면 사라짐 (개발/데모용)
# SqliteSaver  : SQLite 파일   → 재시작해도 유지 (로컬 프로토타입용)
# PostgresSaver: PostgreSQL    → 실제 서비스용 (langgraph-checkpoint-postgres)

from langgraph.checkpoint.sqlite import SqliteSaver

DB_PATH = os.path.join(os.path.dirname(__file__), 'checkpoints.db')
with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
    sqlite_app = builder.compile(checkpointer=SqliteSaver(conn))
    config_sql = {'configurable': {'thread_id': 'persistent_demo'}}

    sqlite_app.invoke({'messages': [HumanMessage(content='내 취미는 독서야.')]}, config=config_sql)
    sqlite_app.invoke({'messages': [HumanMessage(content='내 취미가 뭐야?')]}, config=config_sql)

    # 체크포인트 이력 조회 — 실행 단계마다 스냅샷이 쌓여 있다
    checkpoints = list(sqlite_app.get_state_history(config_sql))

    # Time-Travel: 과거 체크포인트 config로 invoke하면 그 시점에서 다른 흐름으로 재실행
    past_config = checkpoints[-1].config      # 가장 오래된 체크포인트
    result_tt = sqlite_app.invoke(
        {'messages': [HumanMessage(content='독서 말고 다른 취미도 있어?')]},
        config=past_config,
    )
```

- 그래프 코드는 그대로 두고 **`compile(checkpointer=...)`만 바꾸면** 메모리→SQLite→Postgres로 영속성이 업그레이드된다.
- `get_state_history()`가 체크포인트(각 단계의 State 스냅샷) 목록을 반환한다. 각 항목의 `config`에 `checkpoint_id`가 들어 있다.
- **Time-Travel** = 과거 체크포인트의 config로 다시 invoke → 그 시점의 State에서 분기해 다른 미래를 실행. 디버깅("여기서 다른 입력이었다면?")과 대화 되돌리기의 원리.

### 장기 기억 — Checkpointer vs Store (`03_memory_store.py`)

```python
# Checkpointer: thread(세션) "안"의 단기 기억 — 대화 흐름 이어가기
# Store       : thread를 "넘어" 공유되는 장기 기억 — 사용자 프로필·선호·중요 사실
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()

def chatbot(state: State) -> dict:
    user_id = state.get('user_id', 'anonymous')
    namespace = ('memories', user_id)          # namespace 튜플로 데이터 논리 분리
    memories = store.search(namespace)         # 이 사용자의 장기 기억 조회
    memory_text = '\n'.join(f'- {m.value["fact"]}' for m in memories) if memories else '없음'

    system_prompt = f"""너는 친절한 AI 어시스턴트야.
사용자에 대해 알고 있는 정보:
{memory_text}
대화 중 사용자의 중요한 정보(이름, 취미, 직업 등)가 나오면,
"[기억 저장: <내용>]" 형식으로 메시지 앞에 표시해줘."""

    response = llm.invoke([SystemMessage(content=system_prompt)] + state['messages'])

    # LLM이 표시한 기억을 정규식으로 뽑아 Store에 저장
    if '[기억 저장:' in response.content:
        facts = re.findall(r'\[기억 저장: (.+?)\]', response.content)
        for i, fact in enumerate(facts):
            store.put(namespace, f'fact_{len(memories) + i}', {'fact': fact})
    return {'messages': [response]}

app = builder.compile(checkpointer=MemorySaver(), store=store)   # 둘을 함께 장착

# session_1에서 "나는 이지수야, 취미는 피아노" → session_2(다른 thread)에서도 기억
```

- **무엇을 기억할지 판단하는 것도 LLM에게 시킨다** — 프롬프트 규약(`[기억 저장: ...]`) + 정규식 추출. 교육용으로 명료한 수법이고, 실전에서는 구조화 출력이나 전용 메모리 추출 단계로 견고하게 만든다.
- `namespace=('memories', user_id)` — 사용자별 격리. thread가 달라도 user_id가 같으면 기억이 공유된다.

| | Checkpointer | Store |
|---|---|---|
| 범위 | thread 하나의 대화 흐름 | thread 횡단, 사용자/앱 단위 |
| 기억 종류 | 단기 (지금 대화의 State) | 장기 (프로필·선호·사실) |
| 격리 키 | `thread_id` | `namespace` 튜플 (예: 유형+user_id) |
| 예 | "방금 내가 뭐라고 했지?" | "지난주에 말한 내 취미 기억해?" |

### 병렬 실행 — 정적 Fan-out과 동적 Send (`04_parallel_execution.py`)

**패턴 1 — 정적 병렬**: 분기 수가 그래프 설계 시점에 고정.

```python
static_builder.add_edge(START, 'pros')
static_builder.add_edge(START, 'cons')       # START에서 두 갈래 → 동시 실행 (fan-out)
static_builder.add_edge('pros', 'summary')
static_builder.add_edge('cons', 'summary')   # 둘 다 끝나야 summary 실행 (fan-in)
static_builder.add_edge('summary', END)
```

**패턴 2 — 동적 병렬 (Send API)**: 분기 수가 실행 시점에 결정.

```python
from langgraph.types import Send

class DynamicState(TypedDict):
    queries: list[str]
    results: Annotated[list[str], lambda a, b: a + b]   # 커스텀 reducer — 결과 누적

class WorkerState(TypedDict):
    query: str
    results: Annotated[list[str], lambda a, b: a + b]

def worker_node(state: WorkerState) -> dict:
    result = llm.invoke(f'"{state["query"]}"에 대해 한 문장으로 답해줘.')
    return {'results': [f'[{state["query"]}] {result.content}']}

def fan_out(state: DynamicState) -> list[Send]:
    # 쿼리 수만큼 worker를 병렬 생성 — 각 Send가 (노드명, 그 노드가 받을 state)
    return [Send('worker', {'query': q, 'results': []}) for q in state['queries']]

dynamic_builder.add_node('worker', worker_node)
dynamic_builder.add_conditional_edges(START, fan_out, ['worker'])
dynamic_builder.add_edge('worker', END)

dynamic_app.invoke({'queries': ['LangGraph란?', 'RAG란?', 'MCP란?'], 'results': []})
```

- 정적 병렬의 fan-in이 성립하려면 병렬 노드들이 **서로 다른 필드에 쓰거나 누적 reducer가 있어야** 한다 (같은 필드 덮어쓰기 충돌 방지).
- `Send('worker', state)`는 **워커별로 독립된 입력 state**를 전달한다 — map 연산의 그래프 버전. 결과는 누적 reducer(`lambda a, b: a + b`)로 모인다.
- `add_messages`만 reducer가 아니다 — **임의의 병합 함수를 reducer로 쓸 수 있다**는 것을 이 예제가 보여준다.

---

## 하네스 엔지니어링 (Chapter4/10-harness)

### deepagents + SKILL.md (`agent.py`, `skills/standard-report-format/SKILL.md`)

**하네스(harness) 엔지니어링**: 모델·코드를 바꾸지 않고, 에이전트를 둘러싼 구조물(도구, 파일시스템, 스킬 문서, 시스템 프롬프트)로 행동을 조정하는 접근.

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

# FilesystemBackend: 로컬 파일시스템을 에이전트의 작업 공간으로
# virtual_mode=True: 에이전트에게 /skills/... 같은 가상 경로로 노출 (OS 절대경로 혼동 방지)
backend = FilesystemBackend(root_dir=str(HARNESS_DIR), virtual_mode=True)

agent = create_deep_agent(
    model=ChatOpenAI(model='gpt-5-nano', ...),
    tools=[search_web],
    backend=backend,
    skills=['skills/'],                       # SKILL.md들이 들어 있는 디렉토리
    system_prompt='코드 작성, 수학 계산 등 보고서·리서치 범위를 벗어난 요청은 정중히 거절한다.',
    checkpointer=MemorySaver(),
)

config = {'configurable': {'thread_id': session_id}, 'recursion_limit': 15}
# recursion_limit: LangGraph 노드 실행 횟수 상한 — 기본값 25, 무한루프 방지
for chunk in agent.stream({'messages': [HumanMessage(content=message)]},
                          config=config, stream_mode='values'):
    ...   # 단계마다 메시지 타입·내용 출력해 진행 확인
```

동작 원리 (코드 주석 기준):

1. 에이전트는 각 SKILL.md의 **name + description만 먼저 보고** "이 스킬이 필요하다"를 판단한다
2. 필요하다고 판단하면 `read_file`로 SKILL.md 본문을 읽어 상세 지시를 로드한다
3. 따라서 **SKILL.md만 수정하면 모델·코드 변경 없이 에이전트 동작이 바뀐다**

실습의 스킬 — `standard-report-format/SKILL.md`:

```text
---
name: standard-report-format
description: 외부 교육용 표준 보고서 작성 스킬. 사용자가 "보고서", "리포트", "표준 양식" 등을
  언급하며 작성을 요청할 때 반드시 발동한다. 본 스킬의 EDU-AI-RPT 포맷은 이 파일을 읽어야
  정확히 적용할 수 있다.
---
(본문: [EDU-AI-RPT v1.0] 헤더, ■ TL;DR 3줄, [EDU-1.0]~[EDU-3.0] 섹션 코드,
 "산업 영향도(상/중/하)" 컬럼 표, [EDU-END] 개정 이력 표 — 를 강제하는 템플릿)
```

테스트 케이스 2개가 하네스의 두 축을 검증한다:

- "AI Agent 최신 트렌드를 **표준 보고서 양식**으로 작성해줘" → 모델이 SKILL.md를 읽어야만 EDU-AI-RPT 형식을 알 수 있음 (**스킬 발동 확인**)
- "파이썬으로 퀵소트 코드를 짜줘" → system_prompt의 범위 제한으로 거절 (**가드레일 확인**). 주석: 범위 이탈 거절은 skills의 description만으로는 부족해서 system_prompt로 강제했다.

> **연결 고리** — 프롬프트 엔지니어링이 "말로 시키기"라면 하네스 엔지니어링은 **"환경으로 시키기"**다. 지시가 코드 밖의 문서(SKILL.md)로 나오면, 비개발자도 에이전트 행동을 수정할 수 있고 버전 관리도 문서 단위로 된다.

---

## 관측성과 평가 — Langfuse (Chapter4/11-observability)

### 트레이싱 기초 — CallbackHandler (`01_tracing_basic.py`)

**트레이싱** = LLM 호출의 입력·출력·레이턴시·토큰 수를 자동 기록. Langfuse의 `CallbackHandler`를 체인 실행에 붙이면 코드 수정 없이 모든 단계가 추적된다.

```python
from langfuse import get_client
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()    # .env의 LANGFUSE_* 3종을 자동으로 읽어 인증

chain = prompt | llm | StrOutputParser()
result = chain.invoke(
    {'question': 'LangGraph와 LangChain의 차이를 한 줄로 설명해줘'},
    config={'callbacks': [langfuse_handler]},    # 실행 중 각 단계마다 핸들러 호출
)

langfuse = get_client()
langfuse.flush()    # 큐에 쌓인 이벤트를 서버로 전송 완료 — 스크립트 종료 직전 필수
```

- 사전 준비: cloud.langfuse.com에서 프로젝트 생성 → `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST`를 .env에.
- invoke마다 별도의 trace로 기록되어 대시보드에서 실시간 확인.
- **`flush()`를 빼먹으면 마지막 이벤트가 누락될 수 있다** (전송이 비동기 큐라서).

### LangGraph 트레이싱 — with_config (`02_tracing_langgraph.py`)

```python
app = builder.compile().with_config({'callbacks': [langfuse_handler]})
# 이후 모든 invoke()/stream() 호출에 핸들러 자동 적용
```

- 그래프는 노드·엣지가 많아 호출마다 callbacks를 넘기기 번거롭다 → `with_config`로 **그래프 인스턴스에 기본 config를 고정**.
- 대시보드에서 **어느 노드에서 얼마나 걸렸는지** 단계별로 보인다 — agent → tools → agent 루프가 트리로 펼쳐진다.

### LangChain 밖 추적 — @observe (`03_observe_decorator.py`)

`CallbackHandler`는 LangChain 체인 내부만 추적한다. **일반 파이썬 함수**(RAG의 검색 단계, 전처리, 비즈니스 로직)는 `@observe` 데코레이터로 span을 만든다.

```python
from langfuse import get_client, observe

@observe(name='retrieve-documents')
def retrieve(query: str) -> list[str]: ...

@observe(name='format-context')
def format_context(docs: list[str]) -> str: ...

@observe(name='rag-pipeline')
def rag_pipeline(question: str) -> str:
    docs = retrieve(question)          # 자식 span
    context = format_context(docs)     # 자식 span
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({...}, config={'callbacks': [langfuse_handler]})
    # ↑ CallbackHandler를 여기서도 전달해야 LLM 호출이 같은 트레이스에 묶인다
```

- 중첩 함수에 각각 붙이면 **부모-자식 트리**로 기록된다: rag-pipeline → (retrieve, format, LLM 체인).
- `@observe` 안에서 체인을 부를 때 **CallbackHandler도 같이 넘겨야** 한 트레이스로 합쳐진다 — 둘은 대체제가 아니라 보완재.

### 평가 — 트레이스에 점수 매기기 (`04_evaluation.py`)

트레이싱만으로는 "답변이 좋은지"를 모른다. `create_score()`로 트레이스에 점수를 남겨 품질 추세를 정량 추적한다.

```python
handler1 = CallbackHandler()
answer1 = run_chain('Python 리스트와 튜플의 차이를 설명해줘', handler1)
trace_id1 = handler1.last_trace_id       # 직전 invoke가 만든 trace의 ID

# ① 규칙 기반 — 코드로 판단 (예시 포함 여부)
has_example = any(k in answer1 for k in ['예:', '예를 들어', '예시', '[', '('])
langfuse.create_score(trace_id=trace_id1, name='has-example',
                      value=1.0 if has_example else 0.0, comment='예시 포함 여부 자동 검사')

# ② LLM-as-a-Judge — 다른 LLM이 0.0~1.0 채점
judge_prompt = ChatPromptTemplate.from_messages([
    ('system', '아래 답변의 품질을 0.0~1.0 사이 숫자 하나만 출력하세요. 다른 텍스트는 출력하지 마세요.'),
    ('human', '질문: {question}\n답변: {answer}'),
])
score_str = (judge_prompt | llm | StrOutputParser()).invoke({...})  # judge 호출은 callbacks 미전달(평가용이라 별도 trace 안 만듦)
try:
    score_value = max(0.0, min(1.0, float(score_str.strip())))
except ValueError:
    score_value = 0.5                       # 숫자 파싱 실패 시 중립값
langfuse.create_score(trace_id=trace_id2, name='llm-judge-quality', value=score_value, ...)

# ③ 수동 평가 — 사용자 피드백(👍/👎)을 score로 기록
langfuse.create_score(trace_id=trace_id3, name='user-feedback', value=1.0, comment='사용자 좋아요')
```

| 방식 | 판단 주체 | 장점 | 한계 |
|---|---|---|---|
| 규칙 기반 | 코드 (키워드·길이 등) | 싸고 빠르고 결정적 | 표면적 — 품질의 본질을 못 봄 |
| LLM-as-a-Judge | 다른 LLM | 대규모 자동화, 의미 수준 평가 | judge 비용·편향, 파싱 실패 대비 필요 |
| 수동 | 사람 | 가장 신뢰 | 비싸고 느림, 표본 한정 |

### RAG 다차원 평가 (`05_rag_evaluation_extra.py`)

단일 점수 대신 **3개 차원을 독립 채점**하고, 컨텍스트를 의도적으로 오염시켜 점수가 실제로 달라지는지 검증한다.

```python
class EvalScore(BaseModel):
    correctness: float = Field(description='사실 정확성 0.0~1.0')     # 컨텍스트 기준 사실성
    relevance: float = Field(description='질문과의 관련성 0.0~1.0')   # 질문에 직접 답하는가
    completeness: float = Field(description='답변 완성도 0.0~1.0')    # 핵심 정보 누락 없는가
    reason: str = Field(description='채점 근거 한 줄')

def judge(question, context, answer) -> EvalScore:
    judge_llm = llm.with_structured_output(EvalScore)   # 채점표를 구조화 출력으로 강제
    ...

# @observe로 retrieve → generate를 span 분리, CallbackHandler로 LLM 호출 추적
# 케이스 3종:
#   CASE A — 정확한 컨텍스트(langgraph 문서)       → 고득점 기대
#   CASE B — 빈 컨텍스트(존재하지 않는 doc_key)     → 낮은 관련성 (검색 실패 시뮬레이션)
#   CASE C — 오염된 컨텍스트(날씨 문서)             → 낮은 정확성 (엉뚱한 문서 검색)
# 차원별 점수를 langfuse.create_score()로 각각 기록
```

- 생성 프롬프트가 "컨텍스트만 참고, 없으면 모른다고 하세요"라서 CASE B에서는 모델이 "모른다"고 답하게 된다 — **검색 실패가 환각 대신 정직한 무지로 이어지는지**도 함께 검증되는 셈.
- **평가 케이스를 의도적으로 오염시켜 평가계 자체를 검증**한다 — "채점기가 실제로 나쁜 것을 나쁘다고 하는가"를 확인하는 메타 평가 발상이 이 파일의 백미.

> **연결 고리** — 구조화 출력(`with_structured_output`)이 여기서 세 번째로 등장한다: 영화 리뷰(학습) → Supervisor 라우팅(제어) → 평가 채점표(품질). "LLM의 판단을 프로그램 값으로 받는" 단일 수법이 스택 전체를 관통한다.

---

## 환경과 버전 메모

`requirements.txt` 기준 주요 버전 (2026-08 시점 강의 환경):

| 패키지 | 버전 | 비고 |
|---|---|---|
| langchain | 1.3.14 | `create_agent`는 `langchain.agents`에서 |
| langchain-core | 1.5.3 | Runnable·메시지·프롬프트 |
| langchain-openai | 1.4.1 | ChatOpenAI, OpenAIEmbeddings |
| langchain-community | 0.4.2 | PDFMinerLoader |
| langchain-chroma | 1.1.0 | Chroma 벡터스토어 (chromadb 1.5.9) |
| langgraph | 1.2.10 | StateGraph·Send |
| langgraph-checkpoint-sqlite | 3.1.1 | SqliteSaver |
| langchain-mcp-adapters | 0.3.2 | MultiServerMCPClient |
| mcp / fastmcp | 1.29.0 / 3.4.6 | MCP SDK / 고수준 서버 프레임워크 |
| a2a-sdk | 1.1.2 | protobuf 타입 기반 (1.x) |
| deepagents | 0.7.4 | create_deep_agent, skills |
| langfuse | 4.14.2 | CallbackHandler, @observe, create_score |
| openai | 2.53.0 | Responses API |
| streamlit | 1.61.1 | RAG 챗봇 UI |

- 모델: `gpt-5-nano` (SSAFY GMS 프록시 경유) / 임베딩: `text-embedding-3-small`
- LangChain·LangGraph가 **1.x 세대**다. 인터넷의 예전 자료(0.x — AgentExecutor, initialize_agent, ConversationBufferMemory 등)와 API가 다르므로 검색 시 버전 확인 필수.

## 코드에서 눈여겨볼 점 (📌)

원본 코드를 검토하며 발견한, 그대로 따라 쓰기 전에 알아 둘 지점들. 오류라기보다 대부분 "교육용 단순화"다.

- **주석-코드 불일치 (사소)**: `02_openai.py`와 `02_embeddings.py`의 주석은 "GMS_KEY 환경변수를 자동으로 읽어 인증 — 별도로 api_key를 전달할 필요 없음"이라고 하지만, 실제 코드는 `api_key=os.environ["GMS_KEY"]`를 **명시적으로 전달**한다. (환경변수 자동 인식은 `OPENAI_API_KEY`라는 표준 이름일 때 이야기이고, GMS_KEY라는 커스텀 이름이라 명시 전달이 맞다.)
- **`eval` 2종의 안전성 차이**: `02_tool_calling.py`는 `eval(expression, {'__builtins__': {}})`로 내장함수만 가렸는데, 이것만으로는 완전한 샌드박스가 아니다. `03_tool_node.py`는 문자 화이트리스트(`0123456789+-*/(). `) 검사를 먼저 해 한층 안전하다. 실서비스라면 `ast.literal_eval`이나 전용 수식 파서를 쓸 것. LLM이 만든 문자열을 eval에 넣는 것은 **프롬프트 인젝션이 코드 실행으로 이어질 수 있는** 대표적 위험 지점이다.
- **MCP SSE transport는 레거시 방향**: 실습은 stdio와 SSE 두 모드를 쓰는데, MCP 스펙에서 HTTP 계열의 현행 표준은 Streamable HTTP로 옮겨 가는 추세다(SSE는 하위 호환용). 교육 목적으로는 SSE가 단순해서 좋지만, 새로 만드는 서버라면 전송 방식 선택 시 확인할 것.
- **Streamlit RAG 챗봇은 멀티턴이 아니다**: `st.session_state.messages`는 UI 표시용일 뿐 체인에 주입되지 않는다. 이전 질문을 기억하는 RAG를 원하면 메모리 전략(04·05)과 결합해야 한다.
- **`05_memory_langgraph.py`의 시스템 프롬프트 주입 위치**: 시스템 메시지를 State에 넣지 않고 노드 안에서 `[system] + state['messages']`로 매번 앞에 붙인다. State에 넣으면 `add_messages` 때문에 매 턴 중복 축적되므로 이 방식이 맞다.
- **Supervisor의 로그 메시지 role**: 에이전트 완료 보고를 `SystemMessage`로 messages에 쌓는다. 동작은 하지만 대화 이력에 system 역할이 반복 삽입되는 구조라, 실전에서는 별도 로그 필드나 `AIMessage(name=...)` 쪽이 깔끔하다.
- **`01_tracing_basic.py`·`02_tracing_langgraph.py`의 TODO 주석**: "TODO: ... 전달하세요"라는 실습 과제 주석이 있고 바로 아래에 정답 코드가 채워져 있다 — 수업 중 빈칸 채우기로 진행된 흔적.
- **A2A 클라이언트의 방어적 파싱**: camelCase/snake_case 혼용, task id 위치 6곳 탐색, 결과 텍스트 3단 폴백은 스펙이 아니라 **전환기 구현 편차 대응**이다. SDK가 안정되면 단순해질 코드.
- **하네스의 거절 규칙 위치**: "범위 밖 요청 거절"이 skills description이 아니라 `system_prompt` 인자로 들어간 이유가 주석에 명시돼 있다 — 스킬은 "발동 조건"이지 "금지 규칙"을 강제하는 장치가 아니기 때문.

---

## 다음에 이어서 볼 것

- RAG 고도화: 멀티턴 RAG(메모리 결합), 하이브리드 검색, 리랭킹 — 이번 실습은 기본 골격까지만
- LangGraph의 `interrupt()` 함수형 HITL(이번 실습은 `interrupt_before` 정적 방식)
- PostgresSaver로 실서비스 영속성, Store의 시맨틱 검색(임베딩 기반 장기 기억 검색)
- Langfuse 데이터셋 기반 회귀 평가(프롬프트 바꾸고 전체 테스트셋 재채점)
- 티스토리 발행: 이 노트를 3편으로 나눠 포스팅 (1편 LangChain·RAG / 2편 LangGraph·멀티에이전트 / 3편 MCP·A2A·운영)