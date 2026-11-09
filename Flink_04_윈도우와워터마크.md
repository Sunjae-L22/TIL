# Flink 윈도우로 늦게 도착한 이벤트 집계하기

배송 완료 이벤트가 3초에 발생했지만 11초에 도착했다. 10초 단위 배송 수량을 집계한다면 어느 구간에 넣고, 이미 발표한 숫자는 어떻게 할까? Flink에서는 **윈도우 할당기**가 이벤트의 소속을, **트리거**가 결과를 내는 시점을, **허용 지연**이 발화 뒤 상태를 더 보관할 시간을 정한다.

## 이벤트를 어느 구간에 넣을까?

이벤트 시간은 레코드에 기록된 발생 시각이다. 처리 시간은 Flink 태스크가 레코드를 처리하는 시점의 시스템 시계다. 발생 시각이 3초이고 처리 시각이 11초라면, 크기 10초 텀블링 윈도우에서 이벤트 시간 기준으로는 `[0초, 10초)`, 처리 시간 기준으로는 `[10초, 20초)`에 배정된다. 이 구간 표기에서 시작은 포함하고 끝은 제외한다.

| 유형 | 배정 방식과 예시 |
|---|---|
| 텀블링 | 같은 크기의 창을 겹치지 않게 배치한다. 10초마다 배송 합계를 내면 정확히 10초인 이벤트는 다음 창에 속한다. |
| 슬라이딩 | 창의 크기와 시작점 간격을 따로 정한다. 크기 10초·이동 5초라면 7초 이벤트는 `[0, 10)`과 `[5, 15)` 양쪽에 속한다. |
| 세션 | 같은 키에서 가까이 이어지는 이벤트의 창을 병합한다. 간격이 4초일 때 1초와 3초는 같은 세션, 11초는 별도 세션이다. |
| 글로벌 | 키마다 하나의 창을 사용하거나 전체 입력을 하나로 묶는다. 3건마다 수량을 내보내려면 별도 트리거를 설정한다. |

`key_by`로 창고를 먼저 나누면 시간 구간이 같아도 창고별로 집계한다. 키가 많은 상태에서 슬라이딩 창을 촘촘하게 배치하면 한 이벤트가 여러 집계에 반영되어 상태와 연산 비용이 늘 수 있다. 합계는 `reduce`처럼 점진 집계하는 함수로 누적값만 유지할 수 있다. [Apache Flink · Windows](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/datastream/operators/windows/)

## 트리거는 출력과 내용 초기화를 결정한다

윈도우를 배정하고 나면 트리거가 해당 창의 집계 결과를 언제 계산하거나 내보낼지 결정한다. 이벤트 시간 창의 기본 `EventTimeTrigger`는 워터마크를, 처리 시간 창의 기본 `ProcessingTimeTrigger`는 시스템 시각을 본다. `CountTrigger`는 해당 창의 레코드 개수가 기준을 채울 때 발화한다.

| 반환값 | 결과를 냄 | 집계 내용 초기화 |
|---|---|---|
| `CONTINUE` | 아니요 | 아니요 |
| `FIRE` | 예 | 아니요 |
| `PURGE` | 아니요 | 예 |
| `FIRE_AND_PURGE` | 예 | 예 |

`GlobalWindows`의 기본 트리거는 발화하지 않는다. 예를 들어 `window_all(GlobalWindows.create())`에 `PurgingTrigger.of(CountTrigger.of(3))`를 붙여 수량을 합산하면, `[2, 6, 4, 9]`에서 처음 세 건의 합계 12를 내보내고 집계 내용을 비운다. 네 번째 값 9는 다음 묶음에 남는다. 이 조건에는 마지막 묶음을 강제로 내보내는 규칙이 없다.

시간과 개수 중 먼저 만족하는 조건으로 결과를 내려면 두 조건을 다루는 사용자 정의 트리거가 필요하다. `on_element`는 새 레코드, `on_event_time`과 `on_processing_time`은 등록한 타이머를 처리한다. `clear`는 트리거가 사용한 상태와 타이머를 정리한다. 세션처럼 병합하는 창에서는 병합을 지원하도록 `can_merge`와 `on_merge`도 맞춰야 한다. `PURGE`가 지우는 범위는 창의 집계 내용이며, 창 메타데이터와 트리거 상태의 정리는 별도다. [Apache Flink · Windows — Triggers](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/datastream/operators/windows/#triggers)

## 워터마크는 이벤트 시간이 어디까지 진행됐는지 나타낸다

발생 순서대로 도착한다는 보장이 없으므로, Flink는 워터마크를 이벤트 시간의 진행 기준으로 사용한다. 제한된 순서 뒤바뀜을 가정하는 전략에서는 주기적으로 관측한 최대 이벤트 시각에서 지연 범위와 1ms를 뺀 값을 내보낸다. 예를 들어 최대 시각이 11,000ms이고 지연 범위가 1,000ms면 내보낼 워터마크는 9,999ms다.

![오른쪽으로 흐르는 이벤트 시간 축에 진행 위치를 표시한 워터마크 개념도](images/flink-event-watermark.png)

*청록색 표시가 이벤트 시간의 진행 위치다. 점의 위치는 이벤트 시각을 나타낸다.*

여러 입력 채널을 받는 연산자는 활성 입력의 워터마크 중 가장 작은 값에 맞춰 진행한다. 트래픽이 없는 파티션에서 값이 멈추면 다른 파티션의 레코드가 계속 들어와도 창이 발화하지 않을 수 있다. 일정 시간 레코드가 없는 입력을 진행 계산에서 제외하려면 워터마크 전략에 유휴 감지를 설정한다. [Apache Flink · Generating Watermarks](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/datastream/event-time/generating_watermarks/)

## 한 창에서 5가 나왔다가 9가 되는 이유

10초 이벤트 시간 창 `[0, 10000)`과 허용 지연 3,000ms를 쓰자. 창의 최대 타임스탬프는 9,999ms다. 기본 이벤트 시간 트리거는 워터마크가 이 값에 도달하면 발화한다. Flink 1.20의 시간 창 구현에서 상태 정리 시점은 최대 타임스탬프에 허용 지연을 더한 12,999ms다.

| 연산자가 받은 순서 | 대상 창에서 일어나는 일 |
|---|---|
| 이벤트 시각 1,000ms, 수량 2 | 창에 반영 |
| 이벤트 시각 8,000ms, 수량 3 | 창의 합계가 5 |
| 워터마크 9,999ms | 첫 결과 5 출력 |
| 이벤트 시각 3,000ms, 수량 4 | 창이 남아 있어 합계 9로 갱신하고 재발화 |
| 워터마크 12,999ms | 창 상태 정리 |
| 이벤트 시각 4,000ms, 수량 6 | 정리된 창에 속하므로 설정한 지연 데이터 출력으로 전달 |

위 표는 워터마크와 레코드의 **도착 순서를 고정한 계산 예제**다. 워터마크 전략의 지연 범위는 첫 발화가 얼마나 보수적으로 진행되는지에 영향을 준다. `allowed_lateness`는 발화 뒤 창 상태를 얼마나 오래 유지할지 결정한다. 두 설정 모두 이벤트 시간 진행을 기준으로 설명할 수 있지만, 기준점과 역할이 다르다.

허용 지연의 기본값은 0이다. 너무 늦은 이벤트는 기본 출력에서 제외하며, 별도 `OutputTag`를 연결하면 검토나 재집계에 사용할 수 있다. 재발화한 값 9는 같은 창의 수정된 합계다. 다운스트림에서는 `(창고 ID, 창 시작 시각)` 같은 식별자를 이용해 이전 값 5를 갱신해야 한다. [Apache Flink · Allowed Lateness](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/datastream/operators/windows/#allowed-lateness) · [PyFlink 1.20 · WindowOperator 구현](https://github.com/apache/flink/blob/release-1.20/flink-python/pyflink/fn_execution/datastream/window/window_operator.py)

## PyFlink에서 발화와 지연 데이터 출력을 연결하기

다음 PyFlink 1.20 설정 조각은 `stream`이 `(창고 ID, 수량, 이벤트 시각 ms)` 튜플을 담는 DataStream이라고 가정한다. 합계만 내는 `reduce` 결과에는 창의 시작 시각 필드가 없다. 실제로 upsert 키를 구성할 때는 `ProcessWindowFunction`의 창 문맥에서 시작 시각을 함께 내보낼 수 있다.

```python
from pyflink.common import Duration, Types
from pyflink.common.time import Time
from pyflink.common.watermark_strategy import TimestampAssigner, WatermarkStrategy
from pyflink.datastream.output_tag import OutputTag
from pyflink.datastream.window import TumblingEventTimeWindows


class EventTime(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        return value[2]


watermarks = WatermarkStrategy.for_bounded_out_of_orderness(
    Duration.of_seconds(1)
).with_timestamp_assigner(EventTime())

event_type = Types.TUPLE([Types.STRING(), Types.INT(), Types.LONG()])
late_tag = OutputTag("too-late", event_type)
timed = stream.assign_timestamps_and_watermarks(watermarks)

totals = (
    timed.key_by(lambda event: event[0])
    .window(TumblingEventTimeWindows.of(Time.seconds(10)))
    .allowed_lateness(3000)
    .side_output_late_data(late_tag)
    .reduce(lambda a, b: (a[0], a[1] + b[1], max(a[2], b[2])))
)
too_late = totals.get_side_output(late_tag)
```

코드는 설정 구조를 보여 준다. 위 표처럼 출력 타이밍을 확인할 때는 레코드 목록과 함께 **워터마크를 어느 순서에 전달할지** 정해야 한다. 입력이 빠르게 끝나는 유한 스트림은 중간 워터마크가 기대한 지점에 발행되지 않을 수 있다.

## 복습

- 7초 이벤트는 크기 10초, 이동 5초 창 중 어디에 속하는가?
- 워터마크가 9,999ms와 12,999ms일 때 창의 상태는 각각 어떻게 되는가?
- 같은 창에서 합계 5와 9가 순서대로 나오면 다운스트림은 무엇을 갱신해야 할까?
