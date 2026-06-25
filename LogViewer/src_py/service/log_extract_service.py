"""
Java 대응: com.logviewer.service.LogExtractService

로그 파일에서 조건에 맞는 행을 발췌하여 bytes 로 반환한다.

처리 흐름 (Java와 동일):
  Pass 1) 파일을 한 줄씩 읽어 매칭 행 번호 수집  →  list[MatchResult]
  Build ) MatchResult 목록 → 컨텍스트 적용 → ExtractBlock 목록 → 병합
  Pass 2) 파일을 다시 한 줄씩 읽어 블록 범위 행만 출력

변환 포인트:
    OutputStream 반환     →  bytes 반환 (Flask Response에 바로 전달)
    HttpServletRequest    →  dict params (컨트롤러에서 추출하여 전달)
    IOException           →  Python Exception (try/except)
"""
import os
import configparser
from contextlib import nullcontext
from datetime import datetime
from typing import Optional

from model.log_viewer_config import LogViewerConfig
from model.match_result import MatchResult
from model.extract_block import ExtractBlock


class LogExtractService:
    """Java 대응: public class LogExtractService"""

    # Java: DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
    FILENAME_FORMAT = "%Y%m%d_%H%M%S"

    # =========================================================================
    # 공개 API
    # =========================================================================

    def execute(self, params: dict) -> tuple[bytes, str]:
        """
        Java 대응: public void execute(HttpServletRequest, HttpServletResponse)

        Flask에서는 HttpSer vletResponse 대신 (content, filename) 튜플을 반환.
        컨트롤러가 이 값으로 Response 객체를 만든다.

        Returns:
            (content: bytes,filename: str)
        Raises:
            Exception: 처리 중 오류 발생 시
        """
        config   = self._load_config()
        self._apply_request_params(params, config)

        filename = self._build_filename(config.output_prefix)
        content  = self._extract(config)

        return content, filename

    # =========================================================================
    # Config 로딩 및 파라미터 적용
    # =========================================================================

    def _load_config(self) -> LogViewerConfig:
        """
        Java 대응: private LogViewerConfig loadConfig()
                :  public static LogViewerConfig load() > private static Properties readProperties() 이쪽인듯.

        logviewer.properties 를 읽어 LogViewerConfig 객체를 반환한다.

        로딩 우선순위:
          1) 환경변수 LOGVIEWER_CONFIG_PATH 에 지정된 외부 경로
             Java: System.getProperty("logviewer.config.path")
          2) 이 파일(log_extract_service.py) 기준 상위 폴더의 logviewer.properties
             Java: getClass().getResourceAsStream("/logviewer.properties")

        ── configparser 사용법 ──────────────────────────────────────────────
        .properties 파일에는 섹션 헤더([section])가 없어서 그냥 읽으면 오류 발생.
        → 파일 내용 앞에 더미 섹션 '[DEFAULT]'를 붙여서 읽는 방법을 사용.

        예시:
            with open(path, 'r', encoding='utf-8') as f:
                content = '[DEFAULT]\n' + f.read()
            parser = configparser.RawConfigParser()
            parser.read_string(content)
            value = parser.get('DEFAULT', 'logviewer.file.path', fallback='').strip()
        ────────────────────────────────────────────────────────────────────

        TODO 1: 환경변수 또는 기본 경로에서 .properties 파일 경로를 결정하세요
                힌트: os.environ.get('LOGVIEWER_CONFIG_PATH')
                      os.path.dirname(__file__)  → 현재 파일이 있는 폴더 경로

        TODO 2: configparser 로 파일을 읽고 LogViewerConfig 객체를 채워 return 하세요
        """
        # TODO 1: 설정 파일 경로 결정
        LOGVIEWER_CONFIG_PATH = "logviewer.properties"
        CLASSPATH_DEFAULT     = "./logviewer.properties"

        external_path = os.environ.get('LOGVIEWER_CONFIG_PATH')

        if external_path:
            props_path = external_path
        else:
            props_path = os.path.join(os.path.dirname(__file__), '..', CLASSPATH_DEFAULT)
            # os.path.join("/A/B/C", "file.py")  -> /A/B/C/file.py

        # TODO 2: configparser 로 읽기
        with open(props_path, 'r', encoding='utf-8') as f:
            content = '[DEFAULT]\n' + f.read()
        parser = configparser.RawConfigParser()
        parser.read_string(content)

        # TODO 3: LogViewerConfig 객체 생성 및 필드 채우기
        cfg = LogViewerConfig()
        cfg.file_path          = parser.get('DEFAULT', 'logviewer.file.path',          fallback='').strip()
        cfg.file_encoding      = parser.get('DEFAULT', 'logviewer.file.encoding',      fallback='UTF-8').strip()
        cfg.datetime_condition = parser.get('DEFAULT', 'logviewer.condition.datetime', fallback='').strip()
        cfg.context_lines      = self._parse_context_lines(parser.get('DEFAULT', 'logviewer.context.lines', fallback='10'))
        cfg.output_prefix      = parser.get('DEFAULT', 'logviewer.output.prefix',      fallback='extract').strip()
        cfg.allowed_base_dir   = parser.get('DEFAULT', 'logviewer.allowed.basedir',    fallback='').strip()
        cfg.keywords           = self._parse_keywords(parser.get('DEFAULT', 'logviewer.condition.keywords', fallback=''))
        return cfg


    def _apply_request_params(self, params: dict, config: LogViewerConfig) -> None:
        """
        Java 대응: private void applyRequestParams(HttpServletRequest, LogViewerConfig)

        요청 파라미터가 있으면 config 필드를 덮어쓴다.

        Java 원본:
            String filePath = trim(request.getParameter("filePath"));
            if (!filePath.isEmpty()) config.filePath = filePath;

        Python 대응:
            file_path = params.get('filePath', '').strip()
            if file_path:
                config.file_path = file_path

        TODO: filePath, datetimeCondition, contextLines, keywords 4개 파라미터 처리
        """
        # TODO: 구현
        file_path = params.get('filePath', '').strip()
        if file_path:
            config.file_path = file_path

        datetime_condition = params.get('datetimeCondition', '').strip()
        if datetime_condition:
            config.datetime_condition = datetime_condition

        context_lines = params.get('contextLines', '').strip()
        if context_lines:
            config.context_lines = int(context_lines)

        keywords = params.get('keywords', ' ').strip()
        if keywords:
           config.keywords = config._parse_keywords(keywords)


    # =========================================================================
    # 발췌 처리
    # =========================================================================

    def _extract(self, config: LogViewerConfig) -> bytes:
        """
        Java 대응: private void extract(LogViewerConfig, OutputStream)

        Python에서는 OutputStream 대신 bytes 를 반환한다.
        """
        self._validate_path(config.file_path, config.allowed_base_dir)
        self._validate_condition(config)

        matches: list[MatchResult] = self._find_matches(config)

        # Java: if (matches.isEmpty())
        if not matches:
            return "조건에 매칭되는 로그 라인이 없습니다.\n".encode('utf-8')

        blocks: list[ExtractBlock] = self._build_blocks(matches, config.context_lines)
        merged: list[ExtractBlock] = self._merge_blocks(blocks)

        return self._write_extract(config.file_path, config.file_encoding, merged)

    def _validate_path(self, file_path: str, allowed_base_dir: str) -> None:
        """
        Java 대응: private void validatePath(String, String)

        Java 원본 로직:
            Path normalized = Paths.get(filePath).normalize().toAbsolutePath();
            if (!normalized.startsWith(baseDir)) throw ...
            if (!Files.exists(normalized))        throw ...
            if (!Files.isReadable(normalized))    throw ...

        Python 대응:
            os.path.abspath(file_path)        ← normalize + toAbsolutePath
            normalized.startswith(base_dir)   ← normalized.startsWith(baseDir)
            os.path.exists(normalized)        ← Files.exists(normalized)
            os.access(normalized, os.R_OK)    ← Files.isReadable(normalized)

        TODO: 경로 유효성 검사 구현
              오류 시 raise Exception("메시지")  →  Java: throw new IOException("메시지")
        """
        # TODO: 구현

        if not file_path:
            raise Exception("logviewer.file.path 설정이 비어 있습니다.")

        normalized = os.path.abspath(file_path)

        if allowed_base_dir:
            base_dir = os.path.abspath(allowed_base_dir)

            if not normalized.startswith(base_dir):
                raise Exception("허용되지 않은 경로입니다. - file_path: " + file_path)

        if not os.path.exists(normalized):
            raise Exception("파일을 찾을 수 없습니다. - file_path: " + file_path)

        if not os.access(normalized, os.R_OK):
            raise Exception("파일을 읽을 수 없습니다. (권한 부족) - file_path: " + file_path)

    def _validate_condition(self, config: LogViewerConfig) -> None:
        """
        Java 대응: private void validateCondition(LogViewerConfig)

        날짜 조건 또는 키워드 중 하나 이상 설정됐는지 확인.

        Java 원본:
            boolean hasDatetime = !config.datetimeCondition.isEmpty();
            boolean hasKeywords = !config.keywords.isEmpty();
            if (!hasDatetime && !hasKeywords) throw ...

        Python 힌트:
            bool('')        → False   (빈 문자열은 False)
            bool('ERROR')   → True
            bool([])        → False   (빈 리스트는 False)
            bool(['ERROR']) → True

        TODO: 구현
        """
        # TODO:
        has_date_time = bool(config.datetime_condition.strip())
        has_key_words = bool(config.keywords)
        if not has_date_time and not has_key_words:
            raise Exception("날짜조건 or Keyword 중 하나 이상 입력 필요함 ")


    # =========================================================================
    # Pass 1: 매칭 행 수집
    # =========================================================================

    def _find_matches(self, config: LogViewerConfig) -> list[MatchResult]:
        """
        Java 대응: private List<MatchResult> findMatches(LogViewerConfig)

        Java 원본:
            try (BufferedReader reader = ...) {
                String line;
                int lineNumber = 0;
                while ((line = reader.readLine()) != null) {
                    lineNumber++;
                    String matched = matchLine(line, config);
                    if (matched != null) results.add(new MatchResult(lineNumber, matched));
                }
            }

        Python 대응:
            with open(file_path, 'r', encoding=encoding) as f:
                for line_number, line in enumerate(f, start=1):
                    line = line.rstrip('\\n')          ← readLine()은 줄바꿈 제거됨
                    matched = self._match_line(line, config)
                    if matched is not None:             ← Java: if (matched != null)
                        results.append(MatchResult(line_number, matched))

        TODO: 구현
        """
        # 이런 형식도 가능 -> name: str = 'Mike'
        # 이런 형식도 가능2 -> ages: list = [12, 20, 32]
        #                   변수명 : 형식 = 값 형태인듯?

        results: list[MatchResult] = []
        # TODO: 구현
        charset = config.file_encoding
        with open(config.file_path, 'r', encoding=charset) as f:

            # enumerate : Index, value (line) 순서로 출력
            for index, line in enumerate(f, start=1):
                line = line.rstrip('\n')   # 읽어들인 1줄의 오른쪽에서 줄바꿈 문자 제거

                matched = self._match_line(line, config)

                if matched is not None:
                    results.append(MatchResult(index, matched))

        return results

    def _match_line(self, line: str, config: LogViewerConfig) -> Optional[str]:
        """
        Java 대응: private String matchLine(String, LogViewerConfig)

        매칭되면 키워드 반환, 아니면 None 반환
        Java: null 반환  →  Python: None 반환

        조건 조합 규칙 (Java와 동일):
          날짜 + 키워드 : AND 조합
          키워드만      : OR 조합 (하나라도 포함)
          날짜만        : 날짜 문자열 포함 여부

        Java 원본:
            boolean datetimeOk = !hasDatetime || line.contains(config.datetimeCondition);
            if (hasKeywords) {
                for (String keyword : config.keywords) {
                    if (line.contains(keyword) && datetimeOk) return keyword;
                }
                return null;
            }
            return datetimeOk ? config.datetimeCondition : null;

        Python 힌트:
            keyword in line           ←  Java: line.contains(keyword)
            not config.keywords       ←  Java: config.keywords.isEmpty()
            return None               ←  Java: return null
            config.datetime_condition ←  Java: config.datetimeCondition

        TODO: 구현
        """
        # TODO: 구현
        has_date_time = bool(config.datetime_condition.strip())
        has_key_words = bool(config.keywords)

        date_time_ok = not has_date_time or bool(config.datetime_condition in line)

        if has_key_words:
            for kwd in config.keywords:
                if kwd in line and date_time_ok:
                    return kwd
            return None

        # 날짜 조건만 있는 경우
        if date_time_ok:
            return config.datetime_condition
        else:
            return None

    # =========================================================================
    # 블록 구성 및 병합
    # =========================================================================

    def _build_blocks(self, matches: list[MatchResult], context_lines: int) -> list[ExtractBlock]:
        """
        Java 대응: private List<ExtractBlock> buildBlocks(List<MatchResult>, int)

        Java 원본:
            for (MatchResult match : matches) {
                int start = Math.max(1, match.lineNumber - contextLines);
                int end   = match.lineNumber + contextLines;
                List<String> keywords = new ArrayList<>();
                keywords.add(match.matchedKeyword);
                blocks.add(new ExtractBlock(start, end, keywords));
            }

        Python 힌트:
            for match in matches:              ←  Java: for (MatchResult match : matches)
            max(1, match.line_number - ...)    ←  Java: Math.max(1, match.lineNumber - ...)
            ExtractBlock(start, end, [match.matched_keyword])

        TODO: 구현
        """
        blocks: list[ExtractBlock] = []
        # TODO: 구현
        for match in matches:
            start = max(1, match.line_number - context_lines)
            end = match.line_number + context_lines

            blocks.append(ExtractBlock(start, end, [match.matched_keyword]))

        return blocks

    def _merge_blocks(self, blocks: list[ExtractBlock]) -> list[ExtractBlock]:
        """
        Java 대응: private List<ExtractBlock> mergeBlocks(List<ExtractBlock>)

        Java 원본:
            for (ExtractBlock current : blocks) {
                if (merged.isEmpty()) { merged.add(current); continue; }
                ExtractBlock last = merged.get(merged.size() - 1);
                if (last.overlapsOrAdjacent(current)) {
                    last.mergeWith(current);
                } else {
                    merged.add(current);
                }
            }

        Python 힌트:
            if not merged:             ←  Java: if (merged.isEmpty())
            merged[-1]                 ←  Java: merged.get(merged.size() - 1)
            last.overlaps_or_adjacent(current)
            last.merge_with(current)

        TODO: 구현
        """
        merged: list[ExtractBlock] = []

        # TODO: 구현
        for current in blocks:
            if not merged:
                merged.append(current)
                continue

            last = merged[-1]
            if(last.overlaps_or_adjacent(current)):
                last.merge_with(current)
            else:
                merged.append(current)

        return merged

    # =========================================================================
    # Pass 2: 발췌 내용 출력
    # =========================================================================

    def _write_extract(self, file_path: str, file_encoding: str, blocks: list[ExtractBlock]) -> bytes:
        """
        Java 대응: private void writeExtract(String, String, List<ExtractBlock>, OutputStream)

        Python에서는 OutputStream 대신 문자열 리스트에 모아 bytes 로 반환한다.

        Java 원본 흐름:
            int currentLine = 0;
            for (ExtractBlock block : blocks) {
                // block.startRow 전까지 건너뜀
                while (currentLine < block.startRow - 1) {
                    if (reader.readLine() == null) { writer.flush(); return; }
                    currentLine++;
                }
                writer.println(buildHeader(block));
                // 블록 범위 행 출력
                while (currentLine < block.endRow) {
                    String line = reader.readLine();
                    if (line == null) break;
                    currentLine++;
                    writer.println(line);
                }
                writer.println();  // 블록 사이 빈 줄
            }

        Python 힌트:
            output = []                          ← 결과를 모으는 리스트
            output.append(self._build_header(block))
            output.append(line.rstrip('\\n'))
            output.append('')                    ← 블록 사이 빈 줄 (writer.println())
            return '\\n'.join(output).encode('utf-8')  ← bytes 변환

            파일 읽기 (주의: enumerate(f)는 "모든 줄을 한 번씩 자동 순회"하는 패턴이라
            블록 경계마다 건너뛰거나 멈추는 이 메서드와는 안 맞음. Java의 reader.readLine()처럼
            "필요한 시점에 한 줄만 꺼내기"가 가능한 next(f, None)을 쓸 것):

            with open(file_path, 'r', encoding=file_encoding) as f:
                current_line = 0
                for block in blocks:                              # Java: for (ExtractBlock block : blocks)
                    while current_line < block.start_row - 1:      # Java: while (currentLine < block.startRow - 1)
                        line = next(f, None)                       # Java: reader.readLine()
                        if line is None:                           # Java: if (... == null) { ...; return; }
                            return '\\n'.join(output).encode('utf-8')
                        current_line += 1

                    output.append(self._build_header(block))

                    while current_line < block.end_row:            # Java: while (currentLine < block.endRow)
                        line = next(f, None)
                        if line is None:                           # Java: if (line == null) break;
                            break
                        current_line += 1
                        output.append(line.rstrip('\\n'))

                    output.append('')                               # Java: writer.println()

        TODO: 구현
        """
        # TODO: 구현
        output = []

        with open(file_path, 'r', encoding=file_encoding) as f:

           current_line = 0

           for block in blocks:

               # 블록 시작 전 까지 건너뛰기
               while current_line < block.start_row - 1:
                   line = next(f, None)
                   if not line:
                       return '\n'.join(output).encode('utf-8') # 각각의 list 요소를 줄바꿈(\n) 문자로 연결 + utf-8로 Encoding
                   current_line += 1

               output.append(self._build_header(block))

               # 블록 범위 행 출력
               while current_line < block.end_row:
                   line = next(f, None)
                   if not line:
                       break
                   current_line += 1
                   output.append(line.rstrip('\n'))

               output.append('')

        return '\n'.join(output).encode('utf-8')


    # =========================================================================
    # 유틸
    # =========================================================================

    def _build_header(self, block: ExtractBlock) -> str:
        """
        Java 대응: private String buildHeader(ExtractBlock)

        출력 형식: ========== [Row: 1-20 / Keyword: "ERROR", "NullPointer"] ==========

        Java 원본:
            StringBuilder sb = new StringBuilder("========== [Row: ");
            sb.append(block.startRow).append("-").append(block.endRow);
            sb.append(" / Keyword: ");
            for (int i = 0; i < block.matchedKeywords.size(); i++) {
                if (i > 0) sb.append(", ");
                sb.append('"').append(block.matchedKeywords.get(i)).append('"');
            }
            sb.append("] ==========");

        Python 힌트:
            keywords_str = ', '.join(f'"{kw}"' for kw in block.matched_keywords)
                           ← Java: for loop + StringBuilder
            f-string: f"========== [Row: {block.start_row}-{block.end_row} / Keyword: {keywords_str}] =========="

        TODO: 구현
        """
        sb = "========== [Row:"
        sb += str(block.start_row) + "-" + str(block.end_row)
        sb += " / keyword: "

        for i in range(len(block.matched_keywords)):
            if i>0:
                sb += ", "
            sb += '"' + block.matched_keywords[i] + '"'

        sb += "] =========="
        return str(sb)


    def _build_filename(self, prefix: str) -> str:
        """
        Java 대응: private String buildFilename(String)

        Java 원본:
            return prefix + "_" + LocalDateTime.now().format(FILENAME_FORMAT) + ".log";

        Python 힌트:
            datetime.now().strftime(self.FILENAME_FORMAT)
            ← Java: LocalDateTime.now().format(FILENAME_FORMAT)

        TODO: 구현
        """
        # TODO: 구현
        timestamp = datetime.now().strftime(self.FILENAME_FORMAT)
        return prefix + "_" + timestamp + ".log"


    @staticmethod
    def _parse_keywords(raw: str) -> list[str]:
        """
        Java 대응: private static List<String> parseKeywords(String)

        Java 원본:
            for (String kw : raw.split(",")) {
                String trimmed = kw.trim();
                if (!trimmed.isEmpty()) result.add(trimmed);
            }

        Python 힌트 (한 줄로 표현 가능):
            [kw.strip() for kw in raw.split(',') if kw.strip()]
            ← 이것을 "리스트 컴프리헨션" 이라 부름 (Java의 for + add 를 한 줄로)

        TODO: 구현
        """
        # TODO: 구현
        result = []
        if not raw.strip():
            return result

        return [kw.strip() for kw in raw.split(',') if kw.strip()]


    @staticmethod
    def _parse_context_lines(value: str) -> int:
        """
        Java 대응: private static int parseContextLines(String)

        Java 원본:
            try {
                int n = Integer.parseInt(value.trim());
                return Math.max(0, n);
            } catch (NumberFormatException e) {
                return 10;
            }

        Python 힌트:
            try:
                return max(0, int(value.strip()))  ← Java: Math.max(0, Integer.parseInt(...))
            except ValueError:                     ← Java: catch (NumberFormatException e)
                return 10

        TODO: 구현
        """
        # TODO: 구현

        try:
            contextLine = int(value.strip())
            return max(0, contextLine)

        except:
            return 10


