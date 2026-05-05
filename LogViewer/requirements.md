# requirements.md — LogViewer 기능 요구사항

---

## 배경 및 목적

용량이 큰 `*.log` 파일을 Notepad++ 로 열거나 검색할 때 속도가 느리거나 프리징이 발생한다.
설정 파일에 조회 조건을 미리 정의하고, 단일 URL 호출만으로 조건에 맞는 발췌 파일을 즉시 다운로드받는다.

---

## 핵심 동작 흐름

```
1. 담당자가 설정 파일에 로그 파일 경로, 키워드, 날짜 조건, 컨텍스트 줄 수를 작성한다.
2. 브라우저(또는 HTTP 클라이언트)에서 /logDownload.do 를 호출한다.
3. Java Controller가 설정 파일을 읽어 조건을 파악한다.
4. 지정된 *.log 파일을 라인 단위로 읽으며 조건에 매칭되는 Row를 찾는다.
5. 매칭된 각 Row 기준으로 위아래 N줄을 함께 발췌한다.
6. 인접·중복 발췌 블록은 하나로 합친다.
7. 각 블록 앞에 원본 Row 번호와 매칭된 키워드를 구분자로 삽입한다.
8. 완성된 발췌 내용을 *.log 파일로 즉시 다운로드 응답한다.
```

---

## 기능 요구사항

### F-01. 설정 파일 기반 조건 정의

모든 조회 조건은 설정 파일(`logviewer.properties`)에 작성한다.
별도 UI 화면 없이 설정 파일 수정만으로 조건을 변경한다.

| 항목 | 설명 |
|------|------|
| 로그 파일 경로 | 읽을 `*.log` 파일의 서버 내 절대 경로 |
| 키워드 목록 | 매칭 대상 문자열 (복수 설정 가능) |
| 날짜/시간 조건 | LIKE 방식 문자열 (예: `2024-03-15 09:14`) |
| 컨텍스트 줄 수 | 매칭 Row 기준 위아래 발췌할 줄 수 N |
| 출력 파일명 접두사 | 다운로드 파일명에 사용할 접두사 |

### F-02. 조건 매칭 방식

- **날짜/시간**: 로그 라인에 설정값이 **포함(LIKE)** 되면 매칭.
  범위 지정이 아닌 문자열 포함 여부로 판단하므로,
  `"2024-03-15 09:14"` 설정 시 해당 분(分) 전체가 매칭된다.
- **키워드**: 로그 라인에 해당 문자열이 **포함(LIKE)** 되면 매칭.
  키워드가 복수일 경우 **OR** 조합으로 매칭한다.
- **날짜 + 키워드 동시 설정**: 날짜 조건과 키워드 조건 모두 **AND** 조합으로 적용한다.
  날짜 조건만 단독으로 설정하거나 키워드만 단독으로 설정하는 것도 허용한다.

### F-03. 컨텍스트 라인 발췌

- 매칭된 Row 기준 위 N줄, 아래 N줄을 함께 발췌한다.
- 발췌 블록이 겹치거나 연속되면 하나의 블록으로 병합한다.
- N 값은 설정 파일에서 지정한다.

### F-04. 발췌 파일 구성

각 발췌 블록 앞에 아래 형식의 구분자를 삽입한다:

```
========== [Row: 1021-1031 / Keyword: "user01"] ==========
```

- `Row`: 원본 파일 기준 시작 Row ~ 끝 Row 번호
- `Keyword`: 해당 블록을 발췌하게 한 매칭 키워드 (날짜 조건 단독 매칭 시 날짜 문자열 표시)
- 블록 병합 시 복수 키워드가 매칭된 경우 모두 나열: `"user01", "NullPointerException"`

### F-05. 단일 URL 다운로드

- `/logDownload.do` 한 번의 호출로 설정 파일 읽기 → 발췌 → 파일 다운로드까지 처리한다.
- HTTP 응답 헤더: `Content-Disposition: attachment; filename="extract_20240315_091400.log"`
- 임시 파일을 서버에 저장하지 않고 응답 스트림으로 직접 출력하는 것을 목표로 한다.

---

## 비기능 요구사항

### NF-01. 서버 처리 우선

- 파일 읽기, 조건 매칭, 발췌, 응답 출력 로직은 **전부 Java에서 처리**한다.
- UI는 추후 회사 Framework 적용 시 최소한으로만 구성한다.

### NF-02. 대용량 파일 대응

- 파일 전체를 메모리에 적재하지 않고 **라인 단위 스트리밍** 처리한다.
- `BufferedReader` 기반으로 구현한다.

### NF-03. 보안

- 설정 파일에 지정된 허용 디렉토리 범위 외의 경로 접근을 차단한다 (Path Traversal 방지).
- 설정 파일 자체는 서버 관리자만 편집 가능한 위치에 둔다.

---

## 설정 파일 (`logviewer.properties`)

```properties
# 읽을 로그 파일 경로
logviewer.file.path=/app/logs/application.log

# 날짜/시간 LIKE 조건 (비워두면 전체 날짜 대상)
logviewer.condition.datetime=2024-03-15 09:14

# 키워드 목록 (쉼표 구분, 비워두면 날짜 조건만 적용)
logviewer.condition.keywords=user01,NullPointerException

# 매칭 Row 기준 위아래 발췌 줄 수
logviewer.context.lines=10

# 다운로드 파일명 접두사
logviewer.output.prefix=extract

# 허용 기준 디렉토리 (경로 탐색 방지)
logviewer.allowed.basedir=/app/logs/
```

---

## Controller URL

| URL | HTTP | 역할 |
|-----|------|------|
| `/logDownload.do` | GET | 설정 파일 읽기 → 조건 매칭 → 발췌 파일 다운로드 응답 |

---

## 출력 파일 예시

```
========== [Row: 1021-1031 / Keyword: "user01"] ==========
[2024-03-15 09:14:55] INFO   UserService    - 사용자 로그인 시도: user01
[2024-03-15 09:14:55] ERROR  AuthFilter     - 인증 실패: user01
    at com.example.AuthFilter.doFilter(AuthFilter.java:88)
    at com.example.SecurityChain.proceed(SecurityChain.java:45)
[2024-03-15 09:14:56] WARN   SessionManager - 세션 없음: user01

========== [Row: 3405-3415 / Keyword: "NullPointerException"] ==========
[2024-03-15 09:14:10] ERROR  PaymentService - NullPointerException
    at com.example.PaymentService.process(PaymentService.java:132)
[2024-03-15 09:14:10] ERROR  PaymentService - 결제 처리 중단
```

---

## 구현 우선순위

| 순위 | 항목 |
|------|------|
| 1 | 설정 파일 로딩 (`logviewer.properties` 읽기) |
| 2 | 파일 스트리밍 + 조건 매칭 로직 (Java) |
| 3 | 컨텍스트 발췌 + 블록 병합 로직 (Java) |
| 4 | 다운로드 응답 처리 (`logDownload.do` Controller) |
| 5 | 회사 Framework UI 적용 (내부 Merge 후) |
