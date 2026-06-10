"""
Java 대응: LogViewerConfig (LogExtractService의 Inner Class)

변환 포인트:
    private class LogViewerConfig { ... }  →  @dataclass class LogViewerConfig
    필드 선언 + getter/setter              →  @dataclass 가 __init__ 자동 생성
    List<String> keywords                  →  list[str] keywords
"""
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────
# @dataclass: Java의 DTO처럼 필드 선언만으로 __init__ 자동 생성
# 각 필드에 타입 힌트(: str, : int 등)와 기본값(= ...)을 지정
# ─────────────────────────────────────────────────────────
@dataclass
class LogViewerConfig:
    """
    logviewer.properties 를 읽어 설정값을 보관하는 데이터 클래스.

    Java 필드 대응:
        String       filePath          →  file_path:          str
        String       fileEncoding      →  file_encoding:      str
        String       datetimeCondition →  datetime_condition: str
        List<String> keywords          →  keywords:           list[str]
        int          contextLines      →  context_lines:      int
        String       outputPrefix      →  output_prefix:      str
        String       allowedBaseDir    →  allowed_base_dir:   str

    Python 명명 관례: Java camelCase → Python snake_case
    """
    file_path:          str       = ""
    file_encoding:      str       = "UTF-8"
    datetime_condition: str       = ""
    keywords:           list[str] = field(default_factory=list)  # Java: new ArrayList<>()
    context_lines:      int       = 10
    output_prefix:      str       = "extract"
    allowed_base_dir:   str       = ""
