# CLAUDE.md

## 응답 스타일
- 반말로 답변할 것 (경어체 사용 금지)

## 학습 목표
- Java로 만든 프로그램을 Python으로 변환하는 방식으로 Python 문법 학습 중
- 현재 대상 프로젝트: `LogViewer` (Java → Python 변환)

## 현재 작업 파일 및 구현 상태 (2026.06.25 기준 — 전체 버그 수정 완료)

전체 흐름: `app.py` → `controller/log_download_controller.py` → `service/log_extract_service.py` → `model/*`

### model/extract_block.py
- `overlaps_or_adjacent` ✅ 구현 완료 (`self.end_row + 1 >= other.start_row`)
  - `return` 뒤에 죽은 코드 `pass` 한 줄 남아있음 (동작엔 영향 없음, 정리 대상으로만 남겨둠)
- `merge_with` ✅ 구현 완료 — `if kw not in self.matched_keywords: self.matched_keywords.append(kw)` 로 수정됨 (`list` 내장 타입 쓰던 버그 해결)

### model/match_result.py, model/log_viewer_config.py
- ✅ 둘 다 템플릿 그대로 완성 상태 (수정 불필요)

### service/log_extract_service.py — 전체 메서드 구현 완료
| 메서드 | 상태 | 비고 |
|---|---|---|
| `_load_config` | ✅ | configparser + `[DEFAULT]` 더미 섹션 처리 |
| `_apply_request_params` | ✅ | `param`→`params` 오타 수정 완료. 4개 필드 모두 처리됨. **남은 리스크**: 컨트롤러가 `request.form.get(key)`를 기본값 없이 호출해서 폼에 해당 필드가 전혀 없으면 `params[key]`가 `None`이 되고, `params.get(key, '')`는 키가 존재하면 기본값을 안 주기 때문에 `.strip()`에서 `AttributeError` 날 수 있음 (Java의 `trim()` 헬퍼가 했던 null 방어가 없음). 폼에 4개 필드가 항상 포함되면 문제 없음 — 실제 폼 구조 확인 필요 |
| `_extract` | ✅ | 정상 |
| `_validate_path` | ✅ | 조건 반전 문제 해결, `normalized.startswith(base_dir)` 경로 탈출 방지 체크 추가됨 |
| `_validate_condition` | ✅ | |
| `_find_matches` | ✅ | self 중복 전달 수정, `MatchResult` 객체 감싸기 적용, `index`로 줄번호 정상 기록, `rstrip('\n')`도 실제 줄바꿈 문자로 수정 완료 |
| `_match_line` | ✅ | |
| `_build_blocks` | ✅ | |
| `_merge_blocks` | ✅ | |
| `_write_extract` | ✅ | `for block in blocks`를 바깥 루프로, `next(f, None)`으로 Java의 `readLine()`처럼 필요한 시점에 한 줄씩 꺼내는 구조로 변경. 헤더 중복 출력/무한루프/list 반환 3개 버그 모두 해결, `return '\n'.join(output).encode('utf-8')`로 정상 반환 |
| `_build_header` | ✅ | 키워드 양쪽에 닫는 `"` 추가 완료 |
| `_build_filename` | ✅ | |
| `_parse_keywords` | ✅ | |
| `_parse_context_lines` | ✅ | |

### controller/log_download_controller.py — 완료
- import 오류 수정 완료, TODO 1~3 모두 구현 완료
- `mimetype='text/plain; charset=utf-8'` 세미콜론 추가 완료
- except 블록 정상 동작 (`[Error]` 메시지, 기능상 문제 없음)

### logviewer.properties
- `logviewer.file.path=../logs/sample.log` 로 상대경로 변경됨 (LogViewer 루트 기준 `log/` 디렉토리 활용 추정)

## 다음에 할 일 (우선순위 순, 2026.06.25 갱신)
1. **`python app.py` 실행 → 브라우저로 실제 다운로드 테스트** — 코드 레벨 버그는 다 해결됐으니 이제 실제 동작 확인 단계
2. `_apply_request_params`의 `None.strip()` 리스크 — 테스트 중 폼 필드 누락 시 에러나면 그때 가드 추가 (`request.form.get(key, '')`처럼 컨트롤러 쪽에 기본값 주는 것도 방법)
3. `extract_block.py`의 죽은 코드 `pass` 정리 (선택사항, 동작엔 영향 없음)

## Java → Python 주요 변환 포인트
| Java | Python (Flask) |
|---|---|
| `@Controller` | `Blueprint` |
| `@RequestMapping` | `@bp.route(...)` |
| `HttpServletRequest` | Flask 전역 `request` 객체 |
| `HttpServletResponse` | `return Response(...)` |
| `String.format(...)` | f-string: `f"값: {변수}"` |

## 오늘 다룬 Python 개념

### os.path.join과 `..`
- `'..'`는 경로 문자열에 그대로 포함됨 (상위 디렉토리 이동)
- 정규화하려면 `os.path.normpath()` 사용

### Flask Response vs requests
- `Response(content, status=200, mimetype='...')` → 서버가 클라이언트에게 응답 반환
- `requests.get(URL)` → 클라이언트가 외부 서버에 요청 (역할이 반대)
- status code 지정: `Response(..., status=500)` 또는 `response.status_code = 200`

### pass 키워드
- 블록이 비어있을 때 SyntaxError 방지용 플레이스홀더
- 실제 구현 코드가 들어오면 삭제하는 게 관례
- `return` 뒤에 남겨둔 `pass`는 절대 실행되지 않는 죽은 코드 (에러는 아니지만 정리 대상)

### f-string vs 파일 핸들 `f`
- `f"문자열 {변수}"` → f-string (문자열 포맷팅, Java의 String.format과 동일)
- `with open(...) as f:` → 파일 객체를 `f`라는 변수명으로 받는 것 (관행적 약칭)
- `f.read()` → 파일 객체의 메서드 호출

### 함수의 다중 반환값 (튜플)
- `return content, filename` → 사실은 튜플 `(content, filename)`을 반환하는 것
- 받는 쪽: `content, filename = extract_service.execute(params)` → 튜플 언패킹
- Java는 다중 반환이 안 되어 DTO/배열로 감싸야 하지만 Python은 튜플로 바로 가능

### enumerate(f, start=1)
- 파일 객체를 순회하면 (줄번호, 줄내용) 형태로 같이 받을 수 있음
- `for index, line in enumerate(f, start=1):` → Java의 `readLine()` + 수동 카운터 증가를 한 줄로

### list.append()는 인자 1개만 받는다
- `results.append(index, matched)` 처럼 인자 2개 넣으면 TypeError
- 객체로 묶어서 1개로 만들어야 함: `results.append(MatchResult(index, matched))`

### while vs if — 조건이 안 바뀌면 while은 무한루프
- `if`는 한 번만 검사하고 지나가지만, `while`은 조건이 거짓이 될 때까지 반복
- 루프 안에서 조건에 쓰인 변수를 바꿔주지 않으면 영원히 끝나지 않음 (`_write_extract`에서 실제로 겪은 버그)

### 문자열 + 숫자는 직접 연결 불가
- Java: `"" + 5` 는 자동으로 문자열 변환됨
- Python: `"" + 5` 는 TypeError. `str(5)` 또는 f-string으로 변환 필요

### f-string 안에서 따옴표 중첩 주의
- `f'... {x}, mimetype='text/plain'` 처럼 같은 종류의 따옴표를 안에서 또 열면 문자열이 거기서 끊겨버려 SyntaxError 발생
- 안쪽 따옴표는 바깥과 다른 종류(`'` vs `"`)를 쓰거나, f-string을 별도 변수로 분리할 것

## Java 프로젝트 실행 준비 (LogViewer)

### 프로젝트 구조
- IntelliJ 모듈 타입: `JAVA_EE_MODULE` (Dynamic Web Project 설정 이미 되어있음)
- JDK 11, Spring MVC 5.3.39, Tomcat 9 기반
- `web/WEB-INF/dispatcher-servlet.xml`, `web/WEB-INF/web.xml` 존재

### 현재 상태
| 항목 | 상태 |
|---|---|
| JDK 11 | 설치됨 |
| Tomcat 9.0.117 | 다운로드 완료, `C:\selfStudy\server\apache-tomcat-9.0.117\` 에 배치 필요 |
| Spring 5.3.39 JAR 8개 | 미준비 (내일 진행 예정) |

### 필요한 Spring JAR 목록 (web/WEB-INF/lib/ 에 배치)
- spring-webmvc-5.3.39.jar
- spring-context-5.3.39.jar
- spring-core-5.3.39.jar
- spring-beans-5.3.39.jar
- spring-web-5.3.39.jar
- spring-aop-5.3.39.jar
- spring-expression-5.3.39.jar
- spring-jcl-5.3.39.jar

### JAR 다운로드 방법
- mvnrepository.com 에서 직접 검색하여 다운로드
- 또는 Maven CLI: `mvn dependency:get -Dartifact=org.springframework:spring-webmvc:5.3.39`

### Spring JAR 준비 후 IntelliJ Run 설정 순서
1. `Run → Edit Configurations → + → Tomcat Server → Local`
2. `Configure...` 에서 Tomcat 설치 경로 지정
3. `Deployment` 탭 → `+` → `Artifact` → `LogViewer:war exploded` 선택
