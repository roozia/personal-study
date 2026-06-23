# CLAUDE.md

## 응답 스타일
- 반말로 답변할 것 (경어체 사용 금지)

## 학습 목표
- Java로 만든 프로그램을 Python으로 변환하는 방식으로 Python 문법 학습 중
- 현재 대상 프로젝트: `LogViewer` (Java → Python 변환)

## 현재 작업 파일 및 구현 상태 (2026.06.23 기준)

전체 흐름: `app.py` → `controller/log_download_controller.py` → `service/log_extract_service.py` → `model/*`

### model/extract_block.py
- `overlaps_or_adjacent` ✅ 구현 완료 (`self.end_row + 1 >= other.start_row`)
- `merge_with` ❌ 버그 있음
  - `for kw in range(len(other.matched_keywords))` → 인덱스(정수)를 순회하고 있음. 키워드 문자열 자체를 순회해야 함
  - `if kw not in list: list.append(kw)` → `list`는 변수가 아니라 파이썬 내장 타입 이름. `self.matched_keywords`를 써야 함

### model/match_result.py, model/log_viewer_config.py
- ✅ 둘 다 템플릿 그대로 완성 상태 (수정 불필요)

### service/log_extract_service.py
| 메서드 | 상태 | 비고 |
|---|---|---|
| `_load_config` | ✅ 구현됨 | configparser + `[DEFAULT]` 더미 섹션 처리 적용 |
| `_apply_request_params` | ❌ 미구현 | 아직 `pass` 상태 |
| `_extract` | ✅ | 템플릿 그대로, 정상 |
| `_validate_path` | ❌ 미구현 | 아직 `pass` 상태 |
| `_validate_condition` | ✅ 구현 완료 | |
| `_find_matches` | ❌ 버그 | `self._match_line(self, line, config)` — self 중복 전달(TypeError). `results.append(index, matched)` — append는 인자 1개만 가능, `MatchResult(index, matched)` 객체로 감싸서 넣어야 함. `line.rstrip('\\n')` — `\\n`은 백슬래시+n 두 글자, 줄바꿈이 아님 → `'\n'`로 수정 |
| `_match_line` | ❌ 미완성 | 키워드 없이 날짜 조건만 있는 경우의 반환문이 없음. 함수 끝에 `return config.datetime_condition if date_time_ok else None` 필요 |
| `_build_blocks` | ❌ 버그 | `max(1, match.line_number) - context_lines` → 연산자 우선순위 오류. `max(1, match.line_number - context_lines)`가 맞음 |
| `_merge_blocks` | ❌ 버그 | `last = merged[-1]` 이하 로직이 `for` 루프 밖으로 빠져 있음(들여쓰기 문제) → 루프 안으로 이동해야 매 블록마다 병합 판단함 |
| `_write_extract` | ❌ 버그(가장 심각) | 블록 루프가 라인 루프 안에 있어서 매 줄마다 모든 블록 헤더가 중복 출력됨. `while current_line >= block.start_row ...` → 조건이 안 바뀌는 `while`이라 **무한루프 발생**, `if`로 바꿔야 함. 반환형은 `-> bytes`인데 list를 그대로 반환 중 → `'\n'.join(output).encode('utf-8')` 필요 |
| `_build_header` | ❌ 버그 | `block.start_row + "-"` → int와 str 직접 연결 시도(TypeError). 키워드 루프에서 `if i>0` 조건 때문에 0번째 키워드가 누락됨. 닫는 `"` 없음 |
| `_build_filename` | ❌ 오타 | `self.FILENAME_FPRMAT` → `self.FILENAME_FORMAT` (AttributeError) |
| `_parse_keywords` | ✅ 구현 완료 | |
| `_parse_context_lines` | ✅ 구현 완료 | |

### controller/log_download_controller.py
- import 오류(`from Flask` → `from flask`)는 2026.06.22 수정 완료
- 파라미터 수집(TODO 1) ✅ 완료
- 서비스 호출(TODO 2) ✅ 완료
- 응답 반환(TODO 3) ❌ 버그 있음
  - `mimetype='text/plainl charset=utf-8'` → 오타, `'text/plain; charset=utf-8'`로 수정
  - `filename="{file_name}"` → 정의되지 않은 변수 참조(NameError). 실제 변수명은 `filename` (언더스코어 위치 다름)
- except 블록 ❌ **SyntaxError 발생 중** — f-string 안에 따옴표가 중첩되면서 깨짐:
  ```python
  return Response(f'[Error] {str(e)}, status=500, mimetype='text/plain; charset=utf-8')
  ```
  올바른 형태: `return Response(f'[오류] {str(e)}', status=500, mimetype='text/plain; charset=utf-8')`

### logviewer.properties
- `logviewer.file.path=../logs/sample.log` 로 상대경로 변경됨 (LogViewer 루트 기준 `log/` 디렉토리 활용 추정)

## 다음에 할 일 (우선순위 순)
1. `controller/log_download_controller.py`의 except 블록 SyntaxError부터 고친다 — 이게 안 고쳐지면 앱 자체가 import 단계에서 실행 안 됨
2. `_write_extract`의 `while` → `if` 무한루프부터 고친다 — 정상 동작 시에도 멈춰버림
3. `_find_matches`, `_build_blocks`, `_merge_blocks`, `_build_header`, `_build_filename` 순서로 디버깅
4. `_validate_path`, `_apply_request_params` 구현 (아직 손 안 댄 부분)
5. 전부 고친 후 `python app.py` → 브라우저로 실제 다운로드 테스트

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
