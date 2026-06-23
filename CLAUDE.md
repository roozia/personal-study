# CLAUDE.md

## 응답 스타일
- 반말로 답변할 것 (경어체 사용 금지)

## 학습 목표
- Java로 만든 프로그램을 Python으로 변환하는 방식으로 Python 문법 학습 중
- 현재 대상 프로젝트: `LogViewer` (Java → Python 변환)

## 현재 작업 파일
- `LogViewer/src_py/controller/log_download_controller.py` — Flask 컨트롤러 변환 중
- `LogViewer/src_py/service/log_extract_service.py` — 서비스 레이어 변환 중

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

### f-string vs 파일 핸들 `f`
- `f"문자열 {변수}"` → f-string (문자열 포맷팅, Java의 String.format과 동일)
- `with open(...) as f:` → 파일 객체를 `f`라는 변수명으로 받는 것 (관행적 약칭)
- `f.read()` → 파일 객체의 메서드 호출

## 미완성 TODO (log_download_controller.py)
- TODO 3: 다운로드 Response 반환 구현 및 `pass` 제거
- except 블록: 에러 응답 반환 구현 및 `pass` 제거

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
