# Upbit AI Auto Trader

AI 기반 암호화폐 자동매매 봇 (Upbit 거래소)

---

## 프로젝트 개요

OpenAI GPT 모델과 다양한 시장 데이터를 결합하여 **업비트 거래소에서 암호화폐(XRP)를 자동으로 매매**하는 트레이딩 봇이다. 단순 기술적 지표뿐 아니라 뉴스, 공포탐욕지수, 유튜브 분석, 차트 이미지 분석까지 종합하여 AI가 매매 판단을 내린다.

## 핵심 기능

### 1. 멀티소스 데이터 수집

| 데이터 소스 | 설명 | API/도구 |
|---|---|---|
| **OHLCV 차트 데이터** | 30일 일봉 + 24시간 시간봉 | pyupbit |
| **기술적 지표** | RSI, MACD, 볼린저밴드, SMA(5/20/60/120), ATR | ta 라이브러리 |
| **호가 데이터** | 매수/매도 상위 5호가 및 잔량 | pyupbit |
| **공포탐욕지수** | 7일간 추세 포함 | alternative.me API |
| **암호화폐 뉴스** | 최신 뉴스 5건 | SerpAPI (Google News) |
| **차트 이미지 분석** | 업비트 차트 캡처 후 GPT Vision 분석 | Selenium + GPT-4o-mini |
| **유튜브 자막 분석** | 크립토 유튜버 영상 자막 분석 | youtube-transcript-api + GPT-4o-mini |

### 2. AI 매매 판단 (GPT-4o)

- 수집된 모든 데이터를 GPT-4o에 전달하여 매매 의사결정
- 출력 형식: `decision`(buy/sell/hold), `confidence_score`(0-100), `percentage`(매매 비율), `reason`(근거)
- 과거 거래 반성(reflection) 결과를 반영하여 같은 실수 반복 방지

### 3. 거래 비율 동적 조정

- 공포탐욕지수 기반 매매 비율 자동 조정
  - **공포 구간(<=25)**: 매수 비율 +20%, 매도 비율 -20%
  - **탐욕 구간(>=75)**: 매도 비율 +20%, 매수 비율 -20%
- 신뢰도(confidence_score) 70 이상일 때만 실제 매매 실행

### 4. 거래 기록 및 자기 반성 시스템

- **trading_history**: 모든 매매 결정 기록 (결정, 비율, 사유, 잔고 스냅샷)
- **trading_reflection**: AI가 과거 거래를 분석하여 반성 일기 작성
  - 시장 상황 분석, 의사결정 분석, 개선점, 성공률, 학습 포인트
  - 다음 매매 판단 시 반성 내용이 입력으로 재활용됨

## 아키텍처

```
ai_trading() (메인 루프)
├── 1. 현재 투자 상태 조회
├── 2. 호가 데이터 조회
├── 3. OHLCV + 기술적 지표 수집
├── 4. 공포탐욕지수 조회
├── 5. 뉴스 데이터 조회
├── 6. 과거 거래 반성 분석 (GPT-4-turbo)
├── 7. AI 종합 분석 (GPT-4o)
│   ├── 차트 이미지 캡처 & Vision 분석 (GPT-4o-mini)
│   └── 유튜브 자막 분석 (GPT-4o-mini)
└── 8. 매매 실행
```

### 클래스 구조

| 클래스 | 역할 |
|---|---|
| `EnhancedCryptoTrader` | 메인 트레이더. 데이터 수집, AI 분석, 매매 오케스트레이션 |
| `TradeManager` | 매매 실행, 비율 조정, 잔고 조회 |
| `DatabaseManager` | SQLite DB 관리 (거래 기록, 반성 일기) |

## 환경 변수

```env
UPBIT_ACCESS_KEY=     # 업비트 API 액세스 키
UPBIT_SECRET_KEY=     # 업비트 API 시크릿 키
OPENAI_API_KEY=       # OpenAI API 키
SERPAPI_KEY=          # SerpAPI 키 (뉴스 조회)
```

## 의존성

```
pyupbit, ta, openai, python-dotenv, requests,
selenium, Pillow, youtube-transcript-api, sqlite3
```

## 실행

```bash
python autotrade.py
```

현재는 단일 실행 모드. 주석 처리된 `while True` 루프를 활성화하면 **10분 간격 자동 반복 매매** 가능.

## 매매 대상

- 기본 티커: **KRW-XRP** (리플)
- `EnhancedCryptoTrader("KRW-XRP")` 생성자 인자로 변경 가능

## 제약사항 / 참고

- 최소 거래 금액: 5,000 KRW
- `execute_trade`에서 매수 금액이 `krw = 10000`으로 하드코딩되어 있음 (테스트 용도로 추정)
- 차트 캡처에 Headless Chrome 필요 (ChromeDriver 설치 필수)
- OpenAI API 호출이 1회 실행당 최대 4회 발생 (비용 주의)
