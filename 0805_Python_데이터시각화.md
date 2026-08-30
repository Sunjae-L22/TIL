# Python 데이터 시각화 & 전처리

> 출처: `0805_AI Python(3)_데이터 시각화.pdf` (총 65페이지) · 정리일: 2026-08-14
> 페이지 표기는 PDF 물리 페이지 기준 (슬라이드 인쇄 번호와 일치).

## 한눈에 보기

- 데이터 분석 시간의 80%가 왜 전처리에 쓰이는가
- 비교·추이·관계·분포·이상치, 각 상황에 어떤 차트를 고르는가
- Matplotlib 한글 폰트·포매팅·서브플롯의 기본 코드 패턴
- 결측치를 평균·중앙값·최빈값 중 무엇으로 채울지 판단하는 기준
- 타이타닉 데이터로 EDA 흐름(로드 → 조회 → 집계 → 전처리 → 파생변수)을 완주하기

## 목차

1. [전처리가 분석의 8할](#전처리가-분석의-8할) (p.4-5, 13-14)
2. [상황별 차트 선택](#상황별-차트-선택) (p.6-9)
3. [Matplotlib 코드 패턴](#matplotlib-코드-패턴) (p.10-11, 17-18)
4. [Seaborn 통계 시각화](#seaborn-통계-시각화) (p.12)
5. [전처리 도구 상자](#전처리-도구-상자) (p.15-16, 19-24)
6. [타이타닉 EDA 실습](#타이타닉-eda-실습) (p.26-55)
7. [확인 문제](#확인-문제) (p.57-62)
8. [활동 정리](#활동-정리) (p.63-64)

---

## 전처리가 분석의 8할

### 모델링보다 전처리 (p.4-5)

- 데이터 분석 과정에서는 모델링(데이터의 패턴을 학습해 예측이나 분류에 사용할 모델을 만드는 과정)보다 **전처리에 많은 시간이 소요됨** — 전처리 ~80% vs 모델링 ~20%
- **Garbage In, Garbage Out** — 잘못된 데이터를 입력하면 결과도 잘못될 수 있음
- 데이터 전처리: **결측치 보정, 이상치 처리, 정규화, 인코딩**을 수행하는 작업

### 전처리란 (p.13-14)

전처리: **원본 데이터를 분석과 모델 학습에 맞게 다듬는 작업.** 데이터 불러오기 → 전처리 → 분석 → 시각화 → 모델 학습 순서로 진행하며, **원본 데이터는 보존하고 전처리한 사본을 사용**한다.

```text
데이터 수집 → [전처리 (핵심 단계)] → 분석·시각화 → 결과
```

전처리 4대 작업 (p.14, 표 원문):

| 작업 | 문제 상황 | 처리 방법 |
|---|---|---|
| 결측치(Missing Value) | 단가가 비어 있음 | 평균이나 중앙값으로 대체 |
| 이상치(Outlier) | 수량이 99로 입력됨 | 값 확인 후 보정하거나 제거 |
| 정규화(Normalization) | 단가와 수량의 범위가 다름 | 같은 범위로 변환 |
| 인코딩(Encoding) | 메뉴가 문자열로 저장됨 | 숫자 형식으로 변환 |

---

## 상황별 차트 선택

### 왜 그림인가 (p.6-7)

지역 4개 × 메뉴 5개 매출을 숫자표로 보면 패턴이 안 보이지만, 막대 길이로 바꾸면 **범주별 값의 차이를 비교하기 쉬움**.

### 선택 기준표 (p.8-9)

차트를 잘못 지정하면 **데이터 정보를 왜곡하거나 흐리게 만들기 때문에** 유의해야 함 (시계열을 막대로 그리면 추이가 안 보임).

| 데이터 특성 | 추천 차트 | 용도 | 예시 |
|---|---|---|---|
| 범주별 크기 비교 | 막대그래프 bar | 값 비교 | 지역별 매출 |
| 시간에 따른 변화 | 꺾은선그래프 line | 추이 확인 | 월별 매출 변화 |
| 두 변수의 관계 | 산점도 scatter | 관계 확인 | 단가와 수량 |
| 값의 분포와 빈도 | 히스토그램 hist | 분포 확인 | 수량 분포 |
| 범주별 편차와 이상치 | 상자그림 boxplot | 산포와 이상치 확인 | 지역별 매출 분포 |

용어 (슬라이드 각주): **편차(Deviation)** 각 값이 평균과 같은 기준값에서 떨어진 정도 / **산포(Dispersion)** 데이터가 넓게 퍼져 있는 정도 / **시계열(Time Series)** 시간 순서에 따라 기록된 데이터 / **분포(Distribution)** 데이터 값이 어느 구간에 얼마나 나타나는지 보여 주는 형태

> **암기 포인트** — "비교는 bar, 추이는 line, 관계는 scatter, 분포는 hist, 이상치까지 보려면 boxplot." 확인 문제 3개 중 2개가 이 표에서 나왔다.

---

## Matplotlib 코드 패턴

### 한글 폰트 깨짐 해결 (p.10)

기본 폰트에서 한글이 네모로 표시될 수 있다. OS별 폰트는 **Windows Malgun Gothic, macOS AppleGothic, Linux NanumGothic** (p.11). `axes.unicode_minus`를 `False`로 설정하면 음수 부호가 깨지는 현상을 방지할 수 있음.

```python
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'   # Windows 한글 폰트
plt.rcParams['axes.unicode_minus'] = False      # 음수 부호 표시
```

### 기본 차트 그리기 (p.17)

`plt.bar(x, y)` 막대그래프 / `plt.plot(x, y)` 꺾은선그래프 / `title`·`xlabel`·`ylabel` 제목과 축 이름 / `plt.show()` 출력.

```python
지역별매출 = df.groupby('지역')['매출'].sum()

plt.bar(지역별매출.index, 지역별매출.values)
plt.title('지역별 매출')
plt.xlabel('지역'); plt.ylabel('매출')
plt.show()

# 월별 매출 변화
월별매출 = [120, 135, 128, 150, 162]
plt.plot(range(1, 6), 월별매출, marker='o')
plt.title('월별 매출 추이')
plt.show()
```

### 포매팅 요소 한 번에 (p.11)

`plt.legend()` 범례(차트의 색상이나 선이 어떤 데이터를 나타내는지 설명하는 영역) 위치 설정 / `plt.xticks(rotation=45)` x축 글자 45도 회전 / `plt.tight_layout()` 차트 요소가 겹치지 않도록 여백 조정.

```python
plt.figure(figsize=(10, 6))     # 크기 조정
plt.bar(x, y, label='매출')
plt.xlabel('지역', fontsize=12)
plt.ylabel('매출', fontsize=12)
plt.title('지역별 매출', fontsize=14)
plt.legend(loc='upper right')
plt.xticks(rotation=45)
plt.tight_layout()              # 차트 요소가 겹치지 않도록 여백 조정
plt.show()
```

### 서브플롯으로 여러 차트 배치 (p.18)

`plt.subplots(행, 열)`로 차트 영역을 만들고 각 영역은 `axes[행, 열]`로 선택한다. 개별 axes에는 `set_title()`처럼 `set_` 접두어 메서드를 쓴다.

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

지역별매출 = df.groupby('지역')['매출'].sum()
axes[0, 0].bar(지역별매출.index, 지역별매출.values)
axes[0, 0].set_title('지역별 매출')

axes[1, 0].hist(df['수량'], bins=5, edgecolor='black')
axes[1, 0].set_title('수량 분포')

axes[1, 1].scatter(df['단가'], df['수량'])
axes[1, 1].set_title('단가 vs 수량')

plt.tight_layout()
plt.show()
```

---

## Seaborn 통계 시각화

Seaborn: **Matplotlib을 기반으로 통계 차트를 만드는 라이브러리** (p.12). `barplot` 범주별 평균 비교, `boxplot` 값의 분포와 이상치 확인, `heatmap` 상관관계(한 변수가 변할 때 다른 변수가 함께 변하는 정도) 같은 행렬 데이터 표현. 한글은 Matplotlib과 같은 방식으로 폰트를 설정한다.

```python
import seaborn as sns

sns.barplot(data=df, x='지역', y='매출')   # 지역별 평균 매출
sns.boxplot(data=df, x='메뉴', y='매출')   # 메뉴별 매출 분포
sns.heatmap(df.corr(numeric_only=True), annot=True)  # 상관관계
```

> **비교** — `plt.bar`는 넘긴 값을 그대로 그리지만 `sns.barplot`은 범주별 **평균**을 계산해 그린다. 합계를 그리려면 groupby로 집계한 뒤 `plt.bar`에 넘긴다.

---

## 전처리 도구 상자

### 결측치와 이상치 찾기 (p.15)

- `df.isnull().sum()`: 컬럼별 결측치 개수 확인 / `df.describe()`: 최솟값·최댓값 등으로 **이상치의 단서** 확인 (예: age의 max가 320이면 의심)
- 상자그림과 히스토그램으로 분포를 확인하고, **값을 처리하기 전에 결측치와 이상치가 발생한 원인을 확인**

### 분위수 quantile (p.16)

- `quantile()`: 데이터를 크기순으로 나눈 위치의 값을 계산. `quantile(0.9)`는 하위 90%와 상위 10%를 나누는 경계값, `0.25, 0.5, 0.75`는 사분위수, `quantile(0.5)`는 중앙값
- 분위수는 **이상치 판단과 상위 비율 필터**에 사용 — `df.loc[df['매출'] >= df['매출'].quantile(0.9)]` (상위 10% 필터, 실전 적용은 타이타닉 STEP 5)

### 결측치 채우기 fillna (p.19-20)

- `fillna(값)`: 결측치(NaN)를 지정한 값으로 대체. 값을 대체하기 전에 선택한 값이 데이터에 적합한지 확인
- 수치형은 평균 또는 중앙값 — **평균은 이상치에 끌려가므로, 분포가 치우치면 중앙값(median)이 더 안전함**
- 범주형은 최빈값 — **`mode()`는 Series를 반환하므로 첫 번째 값은 `[0]`으로 선택**
- `dropna()`로 결측 행을 통째로 버릴 수도 있으나 데이터 손실에 주의 / `notnull()`: 결측치가 아닌 행을 표시

```python
평균단가 = df['단가'].mean()                  # NaN을 제외하고 평균 계산
df['단가'] = df['단가'].fillna(평균단가)      # 평균으로 채움
df['단가'] = df['단가'].fillna(df['단가'].median())    # 중앙값으로 대체
df['지역'] = df['지역'].fillna(df['지역'].mode()[0])   # 최빈값으로 대체
df.loc[df['단가'].notnull(), '매출'].mean()  # 단가가 있는 행의 매출 평균
```

### category 타입과 범주 추가 (p.21)

- `category`: 정해진 범주를 저장하는 자료형. 반복되는 문자열을 변환하면 **메모리 사용량을 줄일 수 있고, 범주의 순서도 지정 가능**. 변환은 `astype('category')`
- **범주에 없는 값으로 결측치를 대체하려면 해당 값을 범주에 먼저 추가** — `.cat.add_categories('기타')` 후 `fillna('기타')`. 현재 범주 확인은 `.cat.categories`

### 컬럼 삭제, 함수 적용, 구간화 (p.22-24)

- `drop()`: 지정한 컬럼이나 행을 제거. **`axis=1` 컬럼 / `axis=0` 행.** 여러 항목은 목록으로, **원본을 유지하려면 결과를 변수에 저장** — `df = df.drop(['메뉴'], axis=1)`
- `apply()`: 컬럼의 각 값에 함수를 적용해 새로운 값을 생성. 값에 따라 등급이나 코드를 지정할 때 사용. 조건식이 짧으면 lambda(이름 없이 하나의 표현식으로 작성하는 익명 함수)로 작성 가능

```python
def grade(x):
    if x >= 5000:
        return '고가'
    else:
        return '저가'

df['가격대'] = df['단가'].apply(grade)
# lambda 로도 동일: df['단가'].apply(lambda x: '고가' if x >= 5000 else '저가')
```

- 구간화: 연속형 데이터를 여러 구간으로 나누어 범주형 데이터로 변환. 결과는 `value_counts()`로 구간별 개수 확인

| 함수 | 나누는 기준 | 결과 |
|---|---|---|
| `pd.qcut(컬럼, n)` | 각 구간의 **데이터 개수가 비슷하도록** n개 구간 | 동일 빈도 |
| `pd.cut(컬럼, n)` | 값의 **범위를 같은 폭**으로 n개 구간 | 동일 폭 |

> **구분 포인트** — **qcut은 개수를 맞추고, cut은 폭을 맞춘다.** 실습 p.54-55에서 fare를 qcut(5)하면 구간별 172~184개로 균등하지만, age를 cut(10)하면 346개 vs 2개처럼 크게 갈린다.

---

## 타이타닉 EDA 실습

### 탐색적 자료 분석이란 (p.26)

**탐색적 자료 분석(Exploratory Data Analysis)**: 수집한 데이터를 본격적인 분석 전에 그래프나 통계적인 방법으로 **다양한 각도에서 관찰하고 이해하는 과정**. 분포와 값을 검토해 현상을 이해하고, 잠재적인 문제와 패턴을 발견해 **기존 가설을 수정하거나 새로운 가설을 세울 수 있다**. 주요 과정: 분석 목적 설계 및 데이터 확보 → 데이터 탐색(Null, N/A, Outlier 등) → 데이터 값 관찰 및 변환.

### STEP 1~3 목표 설정과 데이터 로드 (p.27-29)

**목표: 타이타닉 호 승객데이터를 기반으로 생존에 영향을 미치는 요인 분석** (기본 EDA → 전처리 → 인사이트 발굴).

```python
import numpy as np
import pandas as pd
import seaborn as sns

df = sns.load_dataset('titanic')
df.head()
```

컬럼 15개 (p.29): **survived**(1 생존, 0 사망), **pclass**(좌석 등급 1·2·3), sex, age, **sibsp**(형제+배우자 수), **parch**(부모+자녀 수), fare(좌석 요금), embarked(탑승 항구 S·C·Q), **who**(man/woman/child), adult_male, **deck**(객실 데크 A~G, 결측 688건), alone(혼자 탑승 여부). **class·embark_town·alive는 각각 pclass·embarked·survived와 같은 정보의 중복 컬럼.**

### STEP 4 기본 데이터 조회 (p.30-32)

```python
df.head()               # 상위 5개 행 (df.tail()은 하위 5개)
df.shape                # (891, 15)
df.info()               # 컬럼별 dtype과 non-null 개수
df.isnull().sum()       # 결측치: age 177, embarked 2, deck 688, embark_town 2
df['survived'].value_counts()   # 0: 549, 1: 342
```

`df.info()`에서 class와 deck는 이미 **category** dtype이다 → 나중에 결측 대체 시 `add_categories`가 필요해지는 복선.

### STEP 5 집계로 생존 패턴 찾기 (p.33-42)

groupby(특정 컬럼을 기준으로 행을 그룹으로 묶어 집계하는 기능)가 기본 패턴. 합계와 비율을 동시에 보려면 `agg`에 리스트를 넘긴다.

```python
df.groupby('embarked')['survived'].sum()    # 항구별 생존자 합계
df.groupby('embarked')['survived'].mean()   # 항구별 생존율
df.groupby('embarked')['survived'].agg(['sum', 'mean'])   # 둘을 한 번에
df.groupby(['sex', 'pclass'])['survived'].agg(['sum', 'mean'])   # 다중 기준
```

기준을 바꿔가며 얻은 결과 (p.33-37):

| 기준 | 결과 (생존자 수 / 생존율) |
|---|---|
| embarked | C 93/0.554 · Q 30/0.390 · S 217/0.337 |
| sex | female 233/**0.742** · male 109/**0.189** |
| alone | False 179/0.506 · True 163/0.304 |
| pclass | 1등급 136/**0.630** · 2등급 87/0.473 · 3등급 119/**0.242** |
| sex+pclass | female 1등급 **0.968** ~ male 3등급 0.135 |
| who+pclass | **child 2등급 1.000** · woman 1등급 0.978 · man 2등급 0.081 |

→ 성별·좌석 등급·동행 여부가 생존율을 크게 갈랐다. "여성과 아이 먼저"가 숫자로 확인된다.

같은 교차 집계는 pivot_table(행과 열의 기준에 따라 값을 교차 집계한 표)로도 얻고 (p.38), groupby 결과는 `reset_index()`로 평평하게 만든 뒤 정렬한다 (p.39):

```python
df.pivot_table(index='sex', columns='pclass',
               values='survived', aggfunc=['sum', 'mean'])

result = df.groupby(['who', 'pclass'])['survived'].agg(['sum', 'mean'])
result = result.reset_index()
result.sort_values(by='mean', ascending=False).reset_index(drop=True)
```

조건 필터 `.loc`와 결합한 질문들 (p.40-42):

```python
# child의 age 범위 → min 0.42, max 15.00
df.loc[df['who'] == 'child', 'age'].agg(['min', 'max'])

# 등급별/연령별 평균 요금
pd.DataFrame(df.groupby(['pclass', 'who'])['fare'].mean())

# 부자는 살았을까? fare 상위 10% 경계값 → 77.9583
rich = df['fare'].quantile(0.9)
df.loc[df['fare'] >= rich, 'survived'].agg(['count', 'mean'])   # count 90, mean 0.766667

# 생존자와 사망자의 평균 나이 → 사망 30.63세, 생존 28.34세
df.groupby('survived')['age'].mean()

# deck 기록 유무별 생존율
df.loc[df['deck'].isnull(), 'survived'].mean()    # 0.2994
df.loc[df['deck'].notnull(), 'survived'].mean()   # 0.6700
```

> **인사이트** — 요금 상위 10%의 생존율(0.767)은 전체 평균(0.384)의 두 배. deck 기록이 **있는** 승객의 생존율(0.670)이 없는 승객(0.299)보다 훨씬 높다. **결측 자체가 정보인 사례** — 객실 기록이 남은 승객은 상급 선실일 가능성이 높다.

### STEP 6 전처리 적용 (p.43-49)

STEP 4에서 확인한 결측치를 컬럼 성격에 맞게 **각각 다른 전략**으로 채우고, `assert`(셀 실행 시 에러가 나지 않아야 함)로 검증한다.

**① embarked — 범주형이므로 최빈값** (p.44)

```python
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])
assert 0 == df['embarked'].isnull().sum()
```

**② age — 성별에 따른 평균으로** (p.45-46). 남자 결측 → 남자 평균(30.73), 여자 결측 → 여자 평균(27.92).

```python
male_mean = df.groupby('sex')['age'].mean()['male']
female_mean = df.groupby('sex')['age'].mean()['female']

df.loc[df['sex'] == 'male', 'age'] = \
    df.loc[df['sex'] == 'male', 'age'].fillna(male_mean)
df.loc[df['sex'] == 'female', 'age'] = \
    df.loc[df['sex'] == 'female', 'age'].fillna(female_mean)

assert 27.92 == round(df.groupby('sex')['age'].mean()['female'], 2)
assert 30.73 == round(df.groupby('sex')['age'].mean()['male'], 2)
```

**③ deck — category 타입이므로 범주 추가 후 'No Data'로** (p.47)

```python
df['deck'] = df['deck'].cat.add_categories('No Data')
df['deck'] = df['deck'].fillna('No Data')
df['deck'].value_counts()   # No Data 688, C 59, B 47, D 33, E 32, A 15, F 13, G 4
```

**④ 중복 컬럼 제거와 특성 공학** (p.48-49). 특성 공학(Feature Engineering): 기존 데이터를 조합하거나 변환해 분석이나 모델링에 사용할 새로운 컬럼을 만드는 작업.

```python
df = df.drop(['class', 'embark_town', 'alive'], axis=1)
df['family'] = df['sibsp'] + df['parch']
```

### 파생변수 EDA와 인코딩 (p.50-55)

새로 만든 family로 생존율을 다시 본다. 정렬해서 TOP 5 / 하위 10 출력 (p.50-52):

```python
result = df.groupby(['sex', 'family'])['survived'].mean()
result = result.reset_index().sort_values('survived', ascending=False)
result.head().reset_index(drop=True)    # 하위 10개는 result.tail(10)
```

→ TOP 5: female family 3(0.842) · 1(0.816) · 0(0.786) · 2(0.776), male 3(0.500). 하위권은 family 4 이상 대가족과 male 단독 탑승(0.156). **가족 1~3명 동반이 유리했고, 대가족(7·10명)은 성별 불문 생존율 0.**

**gender 인코딩** (p.53) — apply로 남자는 1, 여자는 0으로 변경한 gender 컬럼을 생성.

```python
def make_bin(x):
    if x == 'male':
        return 1
    elif x == 'female':
        return 0

df['gender'] = df['sex'].apply(make_bin)
df['gender'].value_counts()   # 1: 577, 0: 314
```

**구간화 적용** (p.54-55) — fare는 **동일한 분포를 갖도록 `pd.qcut`**, age는 **동일한 구간을 갖도록 `pd.cut`**.

```python
df['fare_bin'] = pd.qcut(df['fare'], 5)   # 구간별 172~184개로 균등
df['age_bin'] = pd.cut(df['age'], 10)     # (24.294, 32.252] 346개 vs (72.042, 80.0] 2개
```

---

## 확인 문제

**문제 1** (p.57-58) — 월별 매출의 변화 추이를 확인할 때 적절한 차트는? ① 막대그래프 bar ② 꺾은선그래프 line ③ 산점도 scatter ④ 히스토그램 hist

<details><summary>정답</summary>

**② 꺾은선그래프 line** — 시간에 따른 값의 변화를 확인하므로 정답. 막대는 범주별 값 비교, 산점도는 두 변수의 관계, 히스토그램은 값의 분포 확인용이라 오답.

</details>

**문제 2** (p.59-60) — Matplotlib 그래프에서 한글이 네모로 표시될 때 해결 방법은? ① 그래프의 크기를 키운다 ② 한글 폰트를 지정한다 ③ 데이터를 오름차순으로 정렬한다 ④ plt.show()를 여러 번 호출한다

<details><summary>정답</summary>

**② 한글 폰트를 지정한다** — `rcParams["font.family"]`에 한글 폰트를 설정. 그래프 크기는 폰트의 한글 지원 여부와 무관, 정렬은 순서만 바꾸고, show() 반복 호출은 출력 횟수만 늘어난다.

</details>

**문제 3** (p.61-62) — 수치형 데이터의 분포와 이상치를 확인할 때 적절한 차트는? ① 원그래프 pie ② 상자그림 boxplot ③ 꺾은선그래프 line ④ 막대그래프 bar

<details><summary>정답</summary>

**② 상자그림 boxplot** — 사분위수, 중앙값, 이상치를 함께 표시하므로 정답. 원그래프는 전체에서 각 항목이 차지하는 비율을 나타낸다.

</details>

---

## 활동 정리

핵심 키워드 (p.63, 표 원문):

| 주제 | 키워드 | 핵심 |
|---|---|---|
| Matplotlib 기본 차트 | `bar()`, `plot()`, `scatter()`, `hist()`, 한글 폰트 | 값 비교, 변화 추이, 변수 관계, 분포를 차트로 표현 |
| Seaborn 통계 시각화 | `barplot()`, `boxplot()`, `heatmap()` | 범주별 평균, 값의 분포, 상관관계를 시각화 |
| 데이터 전처리 | `fillna()`, `mode()`, `quantile()` | 결측치와 이상치를 확인하고 평균, 중앙값, 최빈값, 분위수로 처리 |
| 데이터 변환 | `apply()`, `cut()`, `qcut()`, `category` | 함수 적용, 구간화, 범주형 자료형 변환 |
| 탐색적 데이터 분석(EDA) | `describe()`, `groupby()`, `pivot_table()`, `value_counts()` | 데이터를 요약하고 집계해 특징과 패턴을 확인 |

요약 (p.64) — 전처리는 분석과 모델 학습 전에 결측치와 이상치를 처리하고, 범주형 데이터는 필요한 경우 숫자 형식으로 인코딩. `describe()`는 수치형 데이터의 요약 통계, `value_counts()`는 값별 개수, 상자그림과 히스토그램은 이상치와 분포를 확인.

---

## 정리 체크리스트

- [ ] 전처리와 모델링의 시간 비중(80/20)과 Garbage In, Garbage Out을 설명할 수 있다
- [ ] 전처리 4대 작업(결측치·이상치·정규화·인코딩)을 문제 상황과 함께 말할 수 있다
- [ ] 비교/추이/관계/분포/이상치 각각에 맞는 차트를 즉답할 수 있다
- [ ] Matplotlib 한글 폰트 설정 두 줄을 쓸 수 있다
- [ ] 평균/중앙값/최빈값 대체를 각각 어떤 데이터에 쓰는지, `mode()[0]`의 `[0]`이 왜 필요한지 안다
- [ ] category 컬럼에 새 값으로 fillna하기 전에 해야 할 일을 안다
- [ ] qcut과 cut의 차이를 "개수 vs 폭"으로 설명할 수 있다
- [ ] groupby → agg → reset_index → sort_values 체인을 쓸 수 있다
- [ ] deck 결측 여부와 생존율의 관계처럼 "결측 자체가 정보"인 사례를 설명할 수 있다

## 복습 문제

**1.** category 타입인 deck 컬럼의 결측치를 'No Data'로 채우려 한다. 바로 `fillna('No Data')`를 실행하면 안 되는 이유와 올바른 코드를 쓰시오.

<details><summary>답</summary>

category 타입은 **범주에 없는 값으로 결측치를 대체할 수 없으므로**, 해당 값을 범주에 먼저 추가해야 한다.

```python
df['deck'] = df['deck'].cat.add_categories('No Data')
df['deck'] = df['deck'].fillna('No Data')
```

</details>

**2.** `pd.qcut(df['fare'], 5)`와 `pd.cut(df['age'], 10)`의 구간 나누는 기준 차이를 쓰고, 각 결과의 `value_counts()`가 어떤 모양이 되는지 설명하시오.

<details><summary>답</summary>

- `qcut`: 각 구간의 **데이터 개수가 비슷하도록** 나눔 (동일 빈도) → 구간별 172~184개로 균등
- `cut`: 값의 **범위를 같은 폭으로** 나눔 (동일 폭) → 데이터가 몰린 구간(346개)과 거의 없는 구간(2개)이 생김

</details>

**3.** 타이타닉 데이터에서 sex별·pclass별 생존자 합계와 생존율을 한 번의 groupby로 구하는 코드를 쓰시오.

<details><summary>답</summary>

```python
df.groupby(['sex', 'pclass'])['survived'].agg(['sum', 'mean'])
```

같은 결과를 `df.pivot_table(index='sex', columns='pclass', values='survived', aggfunc=['sum', 'mean'])`로도 얻을 수 있다.

</details>

---

> **읽은 방식 메모** — 65페이지 전부를 1100px 렌더링 이미지로 직접 판독했고 OCR은 사용하지 않았다. 모든 코드 블록과 표·출력값은 슬라이드 원문을 육안 대조해 옮겼다. 실습 슬라이드(p.30-55)의 `# 코드를 입력해 주세요` 주석은 빈칸 채우기용 표기라 노트에서는 생략했다. p.16, 21-22, 24의 카페 예시 코드 중 타이타닉 실습(STEP 5-6)에서 동일 패턴이 반복되는 것은 실습 쪽 코드로 대표해 정리했다. 슬라이드 p.50-52의 머리말은 "STEP 6: 전처리"지만 내용은 파생변수 생존율 확인(EDA에 가까움)이어서 별도 소절로 분리했다.
