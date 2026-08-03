# CLAUDE.md

## 응답 스타일
- 반말로 답변할 것 (경어체 사용 금지)

## 학습 목표
- Java로 만든 프로그램을 Python으로 변환하는 방식으로 Python 문법 학습 중
- 현재 대상 프로젝트: `LogViewer` (Java → Python 변환)
- **(2026.07.14~) 신규 학습 방향 전환**: Python 프로젝트를 백지 상태에서 직접 Setup 해보는 연습 (회사에선 항상 세팅된 환경만 써서 초기 세팅 경험이 없음). pytest 테스트 코드 작성도 목표.

## Python Setup 연습 프로젝트 (2026.07.14 시작)

### 목적 / 배경
- 회사에선 항상 세팅 완료된 환경에서만 작업 → venv, pyproject.toml, pytest 등을 **처음부터 손으로** 세팅하는 연습
- 기존 `LogViewer/src_py`에 붙이지 않고 **새 프로젝트**로 백지 시작 (기존은 이미 완성 구조라 "Setup부터" 목적에 안 맞고, sys.path 의존 방식이라 표준 pyproject 구조와 충돌)
- 세팅에 익숙해지면 나중에 LogViewer 로직을 이 구조로 옮겨올 예정

### 프로젝트 위치 / 이름
- `C:\selfStudy\py_setup_logviewer\` (git 루트 `C:\selfStudy`는 유지, 그 하위에 새 폴더)
- 이름은 스네이크 케이스 — Python 패키지/모듈명 표준(PEP 8). 하이픈은 패키지명에 못 씀(`import` 문법 오류)

### 도구 스택 (계획) — Java 대응
| 역할 | Python 도구 | Java 대응 |
|---|---|---|
| 가상환경(격리) | `venv` | Maven local repo(.m2) 개념 |
| 의존성 관리 | `pyproject.toml` | `pom.xml` |
| 테스트 | `pytest` | JUnit |
| 커버리지 | `pytest-cov` | JaCoCo |
| 린터+포맷터 | `ruff` | Checkstyle+SpotBugs |
| 타입 체크(선택) | `mypy` | 컴파일러 타입 검사 |

### 실습 단계 (계획)
1. ✅ 폴더 + venv 생성 + 활성화
2. ✅ 프로젝트 뼈대(src layout) + `pyproject.toml` 작성 + editable 설치
3. ✅ 간단한 함수 1개 + pytest 테스트 1개
4. ✅ `pytest` 실행 → 초록불(3 passed) 확인
5. ✅ ruff, pytest-cov 붙이기 + pyproject에 옵션 박기

## 🎉 5단계 전부 완료 (2026.07.22) — Setup 연습 완주

- 3단계: `keyword_parser.py` + `test_keyword_parser.py` 생성 (아래 확정 내용대로)
- 4단계: `pytest` → `3 passed` 확인
- 5단계: pytest-cov(커버리지) + ruff(린트/포맷) 붙임
  - **pytest-cov**: `pytest --cov=logviewer --cov-report=term-missing` → 100% 확인. 일부러 `raise` 분기 추가해 83%로 떨어뜨리며 `Missing` 컬럼(미실행 줄번호) 체감 → 원복
  - **ruff**: `ruff check`(F401 미사용 import 잡음) + `--fix`(자동 삭제), `ruff format`(작은→큰따옴표 통일, docstring 뒤 빈줄) 체험. `--diff`로 적용 전 미리보기 가능
  - **pyproject.toml에 옵션 박기**: `[tool.pytest.ini_options]`의 `addopts="--cov=logviewer --cov-report=term-missing"`, `testpaths=["tests"]` → 이제 `pytest`만 쳐도 커버리지 자동 출력
- **커밋 완료**: `Python Setup 3~5단계...` (`.coverage`는 재생성물이라 `.gitignore`에 추가 후 제외)

### 방향 확정 (2026.07.24) — 다음 작업은 여기서 시작
- 장기 목표: **특정 현상의 문제점 정의 → MVP 개발** 경험 축적 (회사에선 세팅된 환경만 써서 초기 세팅·구현 전 과정 경험이 부족)
- **결정**: 세팅 반복(후보 A/B) 대신 **작은 MVP 1개를 문제정의부터 끝까지**(후보 C). 세팅은 그 과정에서 "도구"로 소비. 첫 MVP 소재는 **LogViewer 발췌 로직 이식**(익숙한 도메인 → 머리를 "프로세스"에만 씀). 사용자 의사: "1번(LogViewer 이식) 먼저, 그 다음 2번(내가 겪는 실제 불편 자동화)"

### 첫 MVP: LogViewer 로직 → CLI 도구 (2026.07.24 설계 합의)
- **왜 CLI인가 (연습용 아님, 실무 표준)**: 로그 발췌는 전형적 CLI 영역(grep/ripgrep/awk/jq/journalctl/git log). 사내 개발 도구 다수가 CLI. 웹보다 이 도메인에 자연스럽고 새 기술(argparse, `[project.scripts]`)도 붙음
- **진짜 목표 = core 분리**: 순수 로직 core(파일/네트워크 모르는 매칭/블록/병합 함수) ↔ 얇은 껍데기(CLI/Web/라이브러리) 분리. 현재 `LogViewer/src_py`는 로직+파일I/O가 엉겨 테스트 불가 → 이 분리가 MVP 설계 핵심. CLI는 그 분리를 강제하는 좋은 핑계 (나중에 웹 다시 얹고 싶으면 core 위 껍데기만 교체)
- **"이식 = 복붙" 아님**: 복붙은 재료. 연습 본질은 문제정의→설계→구현→테스트 한 바퀴. LogViewer는 도메인 부담 0으로 만드는 재료일 뿐
- **로드맵**: ① 문제 정의 1장 → ② core 분리 설계(순수함수 ↔ I/O) → ③ `src_py` service 로직을 순수함수로 뜯어 `src/logviewer/`로 이식 → ④ 조각마다 pytest(TDD) → ⑤ 3개 기능 test-first로 → ⑥ argparse + `[project.scripts]`로 `logviewer` 명령 등록(**새 세팅 기술: console_scripts 엔트리포인트**)
- **백로그 = 사용자가 직접 추가했던 3개 기능** (`LogViewer/src_py/service/log_extract_service.py` 기준):
  - Story A(대소문자 무시 검색): 332행 `kwd.upper() in line.upper()` → `_match_line`. 순수 판정 → TDD 최적
  - Story B(줄번호 같이 출력): 502행 `str(current_line+1)+" : "+...` → `_write_extract` 출력 포맷
  - Story C(블록 Current/Total 표시): 549행 `Current:.../Total:...` → `_build_header`. 인자→문자열 순수함수, 가장 쉬운 테스트
- **⚠️ Story B 502행에 숨은 버그 (이번 연습 하이라이트)**: `line = str(current_line+1)+" : "+next(f, None)` — 블록 `end_row`가 파일 끝 초과 시 `next`가 `None` 반환 → `str + None`에서 `TypeError`. 아래 `if not line: break` 방어는 연결(+)이 먼저 터져 무력화됨. **지금 손으로 고치지 말 것** → 이식+TDD 단계에서 "이 상황 재현 테스트 먼저(빨간불) → 고쳐서 초록불"로 잡기 = pytest 배우는 이유 그 자체
- **다음 실제 액션**: **사용자가 문제 정의 초안을 직접 작성**(처음이라 손으로 해보고 싶어 함) → 내가 다듬기. 템플릿: 현상 / 불편 / 원하는 것 / MVP 범위·비범위 / 완료 기준. (시간상 다음 세션에 시작 예정)
- **ToDo(나중)**: git CLI로 브랜치 만들기 + PR 날리기 연습. 사용자는 지금껏 Eclipse 등 GUI만 쓰다 최근에야 git 명령줄 사용. 이 MVP를 `git checkout -b feature/...`로 브랜치 따서 작업하고 `gh pr create`로 PR 내면 연습 소재가 됨 → GUI 흐름(브랜치→커밋→PR→머지)의 CLI 1:1 대응을 그때 같이 짚기

### 대화 복구 & PC 이관 방법 (2026.07.24 정리)
- **터미널에서 대화가 휘발돼도 원문은 디스크에 있음**: `C:\Users\user\.claude\projects\C--selfStudy\*.jsonl` (세션 1개=파일 1개, 한 줄=메시지 1개, UTF-8). 화면 표시만 사라진 것. python 덤프 시 한글 깨짐은 터미널 코드페이지 문제지 파일은 멀쩡
  - 이어가기 정공법: `claude --continue`(최근 세션) / `claude --resume`(목록에서 선택)
- **핵심: 대화기록·memory는 git repo 밖(`C:\Users\user\.claude\`)이라 `git push`로 안 딸려감**. 이관 채널 2원화:
  - ① 맥락 → **CLAUDE.md (repo 안, git이 자동 이송)**. 원칙: 중요한 건 반드시 CLAUDE.md에 남긴다. .jsonl은 "혹시 몰라 보관하는 원본"일 뿐 주 채널 아님
  - ② git 밖 자산(memory `MEMORY.md`/`feedback_*.md`, 대화원문 .jsonl)은 **`C:\Users\user\.claude\projects\C--selfStudy\` 폴더를 새 PC로 수동 복사**해야 보존됨. 안 하면 새 PC에서 백지
- **새 메인 PC 세팅 순서(이 PC 포맷 전 1회)**: `git clone <원격>` → `cd py_setup_logviewer` → `py -3.12 -m venv .venv` → `Activate.ps1` → `pip install -e ".[dev]"` → `pytest`(초록불로 이관 검증)
- **✅ 원격 확인 완료 (2026.08.03)**: `origin` = `https://github.com/roozia/personal-study.git`, `main` → `origin/main` 추적 중, unpushed 커밋 없음
  - **서브모듈 있음**: `personal-study01` (`https://github.com/roozia/personal-study01.git`, detached HEAD `b2d9f6f`) → 새 PC에서 clone할 땐 반드시 `git clone --recurse-submodules`. 안 그러면 빈 폴더로 옴
  - 새 PC 복구: `git clone --recurse-submodules <원격> selfStudy` → `cd py_setup_logviewer` → `py -3.12 -m venv .venv` → `Activate.ps1` → `pip install -e ".[dev]"` → `pytest`(3 passed면 이관 성공)
  - `~/.claude/` 수동 백업 시 **`.credentials.json`은 제외** (인증 토큰. 새 PC에서 재로그인하면 재생성됨)

### 초기 진행 기록 (2026.07.14~16)

**1단계 (완료)**
- `py_setup_logviewer` 폴더 생성 완료
- **venv 버전 이슈**: 처음 `python -m venv .venv` 실행 시 PATH 때문에 3.14로 생성됨(지난번 불안정해서 피했던 버전). `pyvenv.cfg`로 발견 → `Remove-Item -Recurse -Force .venv` 후 `py -3.12 -m venv .venv`로 재생성 → 3.12.10으로 확정
- 활성화 성공: `.\.venv\Scripts\Activate.ps1` → 프롬프트에 `(.venv)` 표시됨
  - PowerShell 실행 정책 보안 오류는 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`로 해결(사용자 스코프만)
- 격리 검증 완료: `Get-Command python` → `.venv\Scripts\python.exe` 가리킴, `pip list` → pip만 있는 빈 창고 확인

**2단계 (완료)**
- 폴더 구조 생성: `src/logviewer/__init__.py`(빈 파일), `tests/` (src layout)
- `pyproject.toml` 작성 완료 — `[project]`(메타/의존성), `[project.optional-dependencies]`의 `dev=["pytest>=8.0"]`, `[build-system]`(setuptools), `[tool.setuptools.packages.find] where=["src"]`
  - 작성 중 `[project.optional-dependencies]` 블록이 복붙으로 중복되어 TOML 파싱 에러 → 중복 2줄 삭제로 해결
  - `python -c "import tomllib; ..."`로 파싱 검증 완료
- **editable 설치**: `pip install -e ".[dev]"` 실행 → `Successfully built py_setup_logviewer`, pytest + 전이 의존성(pluggy/iniconfig/packaging/colorama/Pygments) 자동 설치됨
  - `[dev]`를 따옴표로 감싼 이유: PowerShell이 `[ ]`를 특수문자로 해석하는 것 방지

**3단계 (진행 중 — 파일 내용은 아래 확정, 파일 생성만 남음)**
- 만들 파일 2개. 소재는 지난 LogViewer의 `_parse_keywords` 재활용(로직 이미 이해 → pytest 문법에만 집중)

`src/logviewer/keyword_parser.py`:
```python
"""콤마로 구분된 키워드 문자열을 리스트로 변환하는 함수."""


def parse_keywords(raw: str) -> list[str]:
    if not raw.strip():
        return []
    return [kw.strip() for kw in raw.split(',') if kw.strip()]
```

`tests/test_keyword_parser.py`:
```python
"""parse_keywords 함수에 대한 pytest 테스트."""
from logviewer.keyword_parser import parse_keywords


def test_basic_split():
    assert parse_keywords("ERROR, WARN, INFO") == ["ERROR", "WARN", "INFO"]


def test_excludes_empty_items():
    assert parse_keywords("ERROR, , INFO") == ["ERROR", "INFO"]


def test_empty_string_returns_empty_list():
    assert parse_keywords("") == []
```

### 다음 재개 지점 (이어가기)
- 먼저 venv 활성화 확인: `.\.venv\Scripts\Activate.ps1` → `(.venv)` 표시 (다른 PC면 `py -3.12 -m venv .venv` 후 `pip install -e ".[dev]"` 재실행)
- 위 두 파일 생성 → **4단계**: `pytest` 실행해서 초록불(3 passed) 확인
- 그 다음 **5단계**: ruff, pytest-cov 붙이기

### 이번에 익힌 개념 (Setup 연습)
- **src layout**: `src/패키지/` 구조. 루트에서 패키지가 안 보여서 `pip install -e .` 설치를 강제 → 테스트가 "실제 설치된 패키지"를 import하게 됨(로컬 폴더 우연 import 함정 방지). 테스트에서 `from logviewer... ` (not `from src.logviewer...`)로 import되는 게 그 증거
- **editable 설치(`-e`)**: 소스를 복사하지 않고 바로가기로 연결 → 소스 수정 시 재설치 없이 반영
- **전이 의존성(transitive dependency)**: toml엔 `pytest`만 적었는데 pluggy/iniconfig 등이 자동 설치됨 = pytest가 의존하는 부품들을 pip이 자동으로 끌어옴 (Maven이 spring-webmvc 하나로 spring-core 등 딸려오는 것과 동일)
- **pytest 문법 (JUnit 대응)**: 파일명 `test_*.py`/함수명 `test_*` = 자동 발견·실행(`@Test` 불필요), `assert a == b`(=`assertEquals`), 클래스 불필요

### git 관리 — 무엇을 커밋해야 다른 PC에서 동일 재현되나 (2026.07.16)
- **커밋 대상 (동일 재현의 원천)**:
  - `py_setup_logviewer/pyproject.toml` — 가장 중요. 의존성+구조 정의의 단일 진실 원천(pom.xml 역할). 이거 하나로 환경 재구성됨
  - `py_setup_logviewer/src/logviewer/__init__.py` — 패키지 표식
  - `.gitignore`, `CLAUDE.md`
- **커밋 제외 (PC마다 재생성)**: `.venv/`(절대경로 박혀 이식 불가), `src/*.egg-info/`(editable 설치 잔여물) → 둘 다 `.gitignore`에 등록함
- **핵심 원리**: `pyproject.toml`이 single source of truth라 구조가 갈라질 일 없음. 다른 PC에선 손으로 구조 다시 잡는 게 아니라 git 정의대로 재조립: `git pull` → `py -3.12 -m venv .venv` → 활성화 → `pip install -e ".[dev]"`(pyproject 읽어 pytest까지 동일 복원)
- **git은 빈 폴더를 추적 안 함**: 지금 `tests/`가 비어서 커밋해도 다른 PC엔 안 생김. 3단계에서 `tests/test_*.py` 넣으면 그때 자동 추적됨 (그전엔 `mkdir tests` 수동)

## 현재 작업 파일 및 구현 상태 (2026.06.26 기준 — Python 버전 전체 완료, 실제 다운로드 테스트까지 성공)

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

## Python 버전 완료 현황 (2026.06.26)
- `python app.py` 실행 → 브라우저(`http://localhost:8080/logDownloadPy.html`)에서 실제 파일 다운로드까지 정상 동작 **확인 완료**
- 중간에 겪은 환경 이슈: IntelliJ Python SDK를 3.14 → 3.12로 교체하면서 Flask가 새 인터프리터 환경에 없어 `ModuleNotFoundError` 발생 → `Settings → Project: LogViewer → Python Interpreter`에서 flask 재설치로 해결
- `_apply_request_params`의 `None.strip()` 리스크는 실제 테스트에서 문제 없이 지나감 (폼이 4개 필드를 항상 포함해서 보냄) — 더 손볼 필요 없음
- `extract_block.py`의 죽은 코드 `pass` 한 줄만 정리 대상으로 남아있음 (선택사항)

## Flask 앱 전체 구조와 흐름 (2026.06.26 정리)

요청이 들어와서 응답이 나가기까지 전체 흐름:

```
브라우저
  │
  │ ① GET /logDownloadPy.html
  ▼
app.py (index 함수)                  ← HTML 폼 화면만 보여줌
  │
  │ ② 사용자가 폼 작성 후 제출 → POST /logDownloadPy.do
  ▼
controller/log_download_controller.py (download 함수)
  │
  │ ③ params 딕셔너리로 정리해서 넘김
  ▼
service/log_extract_service.py (execute 메서드)
  │
  │ ④ config 로딩 → 검증 → Pass1 매칭 → 블록 생성/병합 → Pass2 출력
  ▼
model/*.py (LogViewerConfig, MatchResult, ExtractBlock)
  │
  │ ⑤ (content, filename) 튜플로 결과 반환
  ▼
controller가 Response 객체로 포장 → 브라우저 파일 다운로드
```

### 각 레이어 역할 요약

| 레이어 | Java 대응 | 역할 |
|---|---|---|
| `app.py` | `DispatcherServlet` + `web.xml` + Tomcat 시작 | 서버 켜기, Blueprint 등록, HTML 서빙 |
| `controller/` | `@Controller` | 요청 받기 → service 위임 → Response 포장 (얇은 레이어, 비즈니스 로직 없음) |
| `service/` | `@Service` | 실제 발췌 로직 전체 담당 |
| `model/` | Inner class / DTO | 데이터 컨테이너 (LogViewerConfig: 설정, MatchResult: 매칭 1건, ExtractBlock: 범위 블록) |

### service 내부 실행 순서

```
execute()
  ├─ _load_config()              → logviewer.properties 읽기
  ├─ _apply_request_params()     → 사용자 입력으로 설정 덮어쓰기
  ├─ _build_filename()           → 다운로드 파일명 생성
  └─ _extract()
       ├─ _validate_path / _validate_condition   → 입력값 검증
       ├─ _find_matches()        → Pass 1: 파일 전체 읽으며 조건 맞는 줄 탐색
       ├─ _build_blocks()        → 매칭 줄 주변에 컨텍스트(앞뒤 줄) 붙이기
       ├─ _merge_blocks()        → 겹치거나 인접한 블록 합치기
       └─ _write_extract()       → Pass 2: 블록 범위에 해당하는 줄만 출력
```

파일을 2번 읽는 이유: Pass1에서 어떤 줄이 조건에 맞는지 먼저 파악하고, 블록 범위 확정 후 Pass2에서 그 범위만 출력. 파일 전체를 메모리에 올리지 않고 대용량 로그 처리 가능.

## (구) 다음 단계 — Java 원본 실행 준비 → **폐기됨**
Java 실행은 다른 PC에서 이미 했던 작업이라 이 PC에서 반복할 이유가 없음. 실제 다음 단계는 위쪽 `### 첫 MVP: LogViewer 로직 → CLI 도구` 참고.

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

### next(iterator, default) — StopIteration 없이 안전하게 한 개씩 꺼내기
- `next(f)`만 쓰면 끝에서 `StopIteration` 예외 발생, `next(f, None)`처럼 기본값을 주면 예외 대신 그 값 반환
- Java의 `reader.readLine()`이 끝에서 `null`을 반환하는 것과 동일한 효과 (`if line is None:` ↔ `if (line == null)`)
- `for line in f` / `enumerate(f)`는 "전체를 한 번에 자동 순회"하는 패턴이라, 블록 경계마다 건너뛰거나 멈추는 로직(`_write_extract`)엔 안 맞음 — 그럴 땐 `next()`로 필요한 시점에만 꺼내 써야 함

### pip 버전 지정 문법과 셸 리다이렉션
- `pip install flask>=3.0.0`처럼 직접 타이핑하면 셸이 `>`를 리다이렉션 기호로 잘못 해석할 수 있음 → `"flask>=3.0.0"`처럼 따옴표 필요
- 이런 문제를 피하려고 `requirements.txt`에 적어두고 `pip install -r requirements.txt`로 설치하는 게 표준 방식

### Python 인터프리터(버전)별로 패키지가 완전히 분리됨
- IntelliJ에서 Python SDK를 3.14 → 3.12로 바꾸면, 이전 버전에 `pip install`했던 flask가 새 인터프리터에는 없음 (서로 별개의 site-packages)
- Java의 JDK 버전을 바꿀 때 클래스패스에 jar를 다시 등록해야 하는 것과 비슷한 개념
- 해결: `Settings → Project → Python Interpreter`에서 새 인터프리터 기준으로 패키지 재설치

### breakpoint() — JS의 debugger;에 대응
- Python 3.7+ 내장 함수, 코드에 `breakpoint()`를 넣으면 그 지점에서 실행이 멈추고 터미널이 pdb 대화형 모드(`(Pdb)`)로 바뀜
- `n`(다음 줄), `s`(함수 안으로), `c`(계속), `p 변수명`(값 출력), `q`(종료)
- 터미널에 직접 `python app.py`를 입력해 실행한 경우에도 동작함 (IDE 연결 여부와 무관)

### IntelliJ 거터 breakpoint는 "Debug" 버튼으로 실행해야 작동함
- 터미널에 `python app.py`를 직접 입력해서 실행하면, IntelliJ가 그 프로세스를 디버그 모드로 인식하지 못해 거터의 빨간 점 breakpoint가 무시됨
- `app.py` 우클릭 → "Debug 'app'" (또는 벌레 아이콘)으로 실행해야 거터 breakpoint가 정상 작동
- 멈춘 후 값 확인은 터미널 명령 없이 Debug 패널의 "Variables"에서 트리로 확인, 변수에 마우스 올리면 툴팁으로도 확인 가능, `Alt+F8`(Evaluate Expression)로 즉석 코드 실행도 가능

### __pycache__ / .pyc 파일
- Python 소스를 실행할 때 자동 생성되는 바이트코드 캐시 (Java의 `.class` 파일과 유사한 역할)
- 실행 시 자동 재생성되므로 git으로 추적할 필요 없음 → `.gitignore`에 `__pycache__/`, `*.pyc` 추가
- `.gitignore` 변경은 로컬에 즉시 반영되지만, 다른 PC에 전파하려면 commit + push 필요

### .iml 파일 이식성
- IntelliJ `.iml` 파일이 `$MODULE_DIR$` 상대경로를 사용하면 다른 PC에서도 그대로 동작
- JDK/Python SDK 이름만 양쪽 IntelliJ에서 일치시키면 모듈 설정 그대로 공유 가능
- `LogViewer.iml`, `misc.xml` → git으로 관리해서 PC 간 IntelliJ 설정 동기화 가능

### HTML이 있는 Flask 앱도 터미널로 실행 가능
- `python app.py` 실행 → 브라우저에서 `http://localhost:8080/logDownloadPy.html` 접속하면 HTML 폼도 정상 동작
- Maven/Gradle은 Java 프로젝트 빌드 도구이므로 Python Flask 실행에는 전혀 불필요

## Java 원본(LogViewer) 위치 — 이 PC에서는 실행 대상 아님 (2026.08.03 정리)
- `LogViewer/src`의 Java 코드는 **다른 PC에서 작성/실행**했던 것. 이 PC에서는 그 소스를 **Python으로 변환하는 재료**로만 썼음
- 따라서 Tomcat 배치 / Spring JAR 8개 준비 / IntelliJ Tomcat Run 설정 절차는 여기서 불필요 → 관련 계획 섹션 삭제함
- `server/apache-tomcat-*`, `web/WEB-INF/lib/`(현재 비어 있음)는 gitignore 대상이라 포맷과 함께 사라져도 무방. 나중에 Java를 다시 돌릴 일이 생기면 그때 새로 받으면 됨
- 정리 내역: 알맹이 없는 `web/web/WEB-INF/web.xml`(304B 껍데기) 삭제 + `LogViewer.iml`에 중복 등록돼 있던 해당 deploymentDescriptor 줄 제거 (진짜 설정은 `web/WEB-INF/web.xml`)
