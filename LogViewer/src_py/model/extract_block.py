"""
Java 대응: ExtractBlock (LogExtractService의 Inner Class)

변환 포인트:
    final int          startRow        →  start_row:        int       (생성 후 변경 불가)
    int                endRow          →  end_row:          int       (mergeWith 에서 변경됨)
    final List<String> matchedKeywords →  matched_keywords: list[str]
"""
from dataclasses import dataclass, field


@dataclass
class ExtractBlock:
    """
    발췌 대상 행 범위 하나를 나타내는 객체.
    startRow / endRow  : 원본 파일 기준 1-based 줄 번호
    matchedKeywords    : 이 블록을 만들어 낸 키워드 목록 (병합 시 누적)

    Java 생성자 대응:
        new ExtractBlock(start, end, keywords)
        →  ExtractBlock(start_row=1, end_row=20, matched_keywords=["ERROR"])
           또는 ExtractBlock(1, 20, ["ERROR"])
    """
    start_row:        int       # Java: final int startRow
    end_row:          int       # Java: int endRow  (mergeWith 에서 변경 가능)
    matched_keywords: list[str] = field(default_factory=list)  # Java: final List<String> matchedKeywords

    def overlaps_or_adjacent(self, other: 'ExtractBlock') -> bool:
        """
        Java 대응: boolean overlapsOrAdjacent(ExtractBlock other)
        두 블록이 겹치거나 바로 인접(1줄 차이)하면 병합 대상으로 판단한다.

        Java 원본:
            return this.endRow + 1 >= other.startRow;

        TODO: Java 조건식을 Python으로 변환하세요
              Java: this.endRow   →  Python: self.end_row
              Java: other.startRow →  Python: other.start_row
        """
        # TODO:
        return self.end_row +1 >= other.start_row
        pass

    def merge_with(self, other: 'ExtractBlock') -> None:
        """
        Java 대응: void mergeWith(ExtractBlock other)
        other 블록을 현재 블록에 흡수한다.

        Java 원본:
            if (other.endRow > this.endRow) {
                this.endRow = other.endRow;
            }
            for (String kw : other.matchedKeywords) {
                if (!this.matchedKeywords.contains(kw)) {
                    this.matchedKeywords.add(kw);
                }
            }

        TODO: Java 로직을 Python으로 변환하세요
              Java: this.endRow = other.endRow  →  Python: self.end_row = other.end_row
              Java: !list.contains(kw)          →  Python: kw not in list
              Java: list.add(kw)                →  Python: list.append(kw)
        """
        # TODO: 구현
        if other.end_row > self.end_row:
            self.end_row = other.end_row

        for kw in other.matched_keywords:
            if kw not in list:
                list.append(kw)


