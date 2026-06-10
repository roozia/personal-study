"""
Java 대응: MatchResult (LogExtractService의 Inner Class)

변환 포인트:
    final int    lineNumber     →  line_number:     int   (불변 필드)
    final String matchedKeyword →  matched_keyword: str   (불변 필드)

    Java에서 final = 재할당 불가
    Python에서는 @dataclass(frozen=True) 로 동일 효과
"""
from dataclasses import dataclass


@dataclass(frozen=True)   # frozen=True → Java의 final 필드와 동일 (변경 불가)
class MatchResult:
    """
    Pass 1 에서 발견된 매칭 라인 하나를 나타내는 객체.

    Java 생성자 대응:
        new MatchResult(lineNumber, matchedKeyword)
        →  MatchResult(line_number=5, matched_keyword="ERROR")
           또는 MatchResult(5, "ERROR")
    """
    line_number:     int   # Java: final int    lineNumber
    matched_keyword: str   # Java: final String matchedKeyword
