# AGENTS.md — LogViewer AI 에이전트 가이드

이 문서는 AI 에이전트가 LogViewer 프로젝트를 이해하고 작업할 때 참고하는 가이드입니다.

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 목적 | 폐쇄망 회사 환경에서 사용할 로그 조회 웹 화면 |
| 배포 형태 | 기존 회사 프로젝트에 소스 Merge (반입신청 후 적용) |
| 실행 환경 | Java 17 또는 18 / Tomcat 9 또는 10 |
| 프레임워크 | 회사 자체 Framework (Java + JavaScript + HTML + Polymer 기반) |
| 호출 방식 | Controller `*.do` URL 패턴으로 로직 실행 |
| 네트워크 | 폐쇄망 — 외부 CDN, npm, Maven Central 등 사용 불가 |

---

## 핵심 제약사항

1. **외부 라이브러리 사용 금지** — 회사 프레임워크가 이미 포함한 라이브러리 외 추가 의존성 없음
2. **Java 17 문법 사용 가능** — records, sealed class, text block 등 허용 (단, 회사 프레임워크와 충돌 없는 범위)
3. **`*.do` 호출 구조 준수** — 단일 URL `/logDownload.do` 로 설정 읽기·발췌·다운로드 완결
4. **Merge 최소화** — 신규 파일 추가 위주, 기존 파일 수정 최소화
5. **반입 신청 가능한 형태** — `.exe` 불가, 소스 파일(`.java`, `.html`, `.js`) 단위로 반입
6. **Python/TypeScript 변환 친화적 코드** — 아래 코딩 컨벤션 참조

---

## 파일 구조 (신규 추가 파일 기준)

```
[회사 프로젝트 루트]
├── src/
│   └── com/logviewer/                         ← 패키지명은 회사 관례로 조정
│       ├── config/
│       │   └── LogViewerConfig.java           # logviewer.properties 로딩 및 설정 DTO
│       ├── model/
│       │   ├── MatchResult.java               # Pass 1 결과: 원본 줄 번호 + 매칭 키워드
│       │   └── ExtractBlock.java              # 발췌 블록: 행 범위 + 키워드 목록 + 병합 로직
│       ├── service/
│       │   └── LogExtractService.java         # 핵심 로직: 두 번 스트리밍으로 발췌 처리
│       └── controller/
│           └── LogDownloadController.java     # /logDownload.do 처리 및 다운로드 응답
│
└── WEB-INF/
    └── classes/
        └── logviewer.properties               # 조회 조건·경로·발췌 줄 수 설정 파일
```

> - 패키지 경로(`com/logviewer`)는 회사 프로젝트 관례에 맞게 조정합니다.
> - `logviewer.properties` 는 클래스패스 루트(`WEB-INF/classes/`) 또는
>   `-Dlogviewer.config.path=<절대경로>` JVM 옵션으로 외부 경로를 지정할 수 있습니다.

---

## Controller URL 패턴

| URL | HTTP | 역할 |
|-----|------|------|
| `/logDownload.do` | GET / POST | 설정 파일 읽기 → 조건 매칭 → 발췌 파일 즉시 다운로드 |

다운로드 응답 헤더:
```
Content-Type: text/plain; charset=UTF-8
Content-Disposition: attachment; filename="extract_20240315_091400.log"
```

---

## 로그 파싱 정규식

대상 로그 형식:
```
[2024-01-01 12:00:00] ERROR  SomeClass  - 오류 메시지
[2024-01-01 12:00:01] INFO   SomeClass  - 정보 메시지
    at com.example.SomeClass.method(SomeClass.java:42)   ← 스택트레이스 라인
```

파싱 정규식 (Java):
```java
// 정상 로그 라인
Pattern LOG_PATTERN = Pattern.compile(
    "^\\[(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})\\]\\s+(\\w+)\\s+(\\S+)\\s+-\\s+(.*)$"
);
// 그룹: 1=timestamp, 2=level, 3=className, 4=message

// 스택트레이스 라인 (앞에 공백)
Pattern STACK_PATTERN = Pattern.compile("^\\s+at .+");
```

---

## 코딩 컨벤션 (Python/TypeScript 변환 친화적)

이 프로젝트는 Java 구현 완료 후 Python → TypeScript 순으로 변환 학습에 활용됩니다.

| 원칙 | 내용 |
|------|------|
| 리플렉션 미사용 | `Class.forName()`, `getDeclaredFields()` 등 금지 |
| 어노테이션 최소화 | 회사 프레임워크 필수 어노테이션 외 커스텀 어노테이션 금지 |
| 상속보다 조합 | 인터페이스 구현은 허용, 다단계 상속 금지 |
| 오버로딩 최소화 | 같은 이름 다른 파라미터 대신 명시적 메서드명 사용 |
| 단순 제네릭 | `List<LogEntry>` 수준만 사용, 와일드카드 지양 |
| 단일 책임 | 각 클래스/메서드는 하나의 역할만 |

주석 작성 규칙 (변환 대상 타입 명시):
```java
// Python: List[LogEntry]
// TS: LogEntry[]
List<LogEntry> entries = new ArrayList<>();

// Python: dict[str, int]
// TS: Record<string, number>
Map<String, Integer> countMap = new HashMap<>();
```

---

## Python / TypeScript 변환 가이드

### 클래스 대응

| Java 클래스 | Python 모듈/클래스 | TypeScript 파일 |
|------------|-------------------|-----------------|
| `LogViewerConfig.java` | `log_viewer_config.py` (dataclass) | `LogViewerConfig.ts` (interface) |
| `MatchResult.java` | `match_result.py` (dataclass) | `MatchResult.ts` (interface) |
| `ExtractBlock.java` | `extract_block.py` (class) | `ExtractBlock.ts` (class) |
| `LogExtractService.java` | `log_extract_service.py` | `logExtractService.ts` |
| `LogDownloadController.java` | (FastAPI router 등으로 대응) | (Express router 등으로 대응) |

### 타입 대응표

| Java | Python | TypeScript |
|------|--------|------------|
| `String` | `str` | `string` |
| `int` | `int` | `number` |
| `boolean` | `bool` | `boolean` |
| `List<T>` | `list[T]` | `T[]` |
| `Map<K,V>` | `dict[K,V]` | `Record<K,V>` |
| `Optional<T>` | `T \| None` | `T \| null` |
| `LocalDateTime` | `datetime` | `string` (ISO 8601) |

### 주요 라이브러리 대응

| Java (표준) | Python | TypeScript (Node.js) |
|------------|--------|---------------------|
| `java.util.regex` | `re` | 내장 `RegExp` |
| `java.io.BufferedReader` | `open()` | `fs.readFileSync()` |
| `java.io.FileWriter` | `open(..., 'w')` | `fs.writeFileSync()` |
| `java.time.LocalDateTime` | `datetime` | `Date` / ISO string |

---

## 반입신청 체크리스트

반입 전 아래 항목을 확인합니다.

- [ ] 신규 추가 파일 목록 정리 완료
- [ ] 외부 라이브러리 의존성 없음 확인
- [ ] 회사 프로젝트 기존 파일 수정 사항 최소화 확인
- [ ] `*.do` URL 패턴 및 패키지명 회사 관례 적용 확인
- [ ] 하드코딩된 로컬 경로 없음 확인 (경로는 설정 또는 파라미터로)
- [ ] 보안 취약점 없음 확인 (경로 탐색, 임의 파일 접근 등)
