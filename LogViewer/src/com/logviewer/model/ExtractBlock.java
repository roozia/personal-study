package com.logviewer.model;

import java.util.List;

/**
 * 발췌 대상 행 범위 하나를 나타내는 객체.
 * startRow / endRow : 원본 파일 기준 1-based 줄 번호
 * matchedKeywords   : 이 블록을 만들어 낸 키워드 목록 (병합 시 누적)
 */
public class ExtractBlock {

    private final int startRow;
    private int endRow;
    // Python: list[str]
    // TS: string[]
    private final List<String> matchedKeywords;

    public ExtractBlock(int startRow, int endRow, List<String> matchedKeywords) {
        this.startRow        = startRow;
        this.endRow          = endRow;
        this.matchedKeywords = matchedKeywords;
    }

    /**
     * 두 블록이 겹치거나 바로 인접(1줄 차이)하면 병합 대상으로 판단한다.
     */
    public boolean overlapsOrAdjacent(ExtractBlock other) {
        return this.endRow + 1 >= other.startRow;
    }

    /**
     * other 블록을 현재 블록에 흡수한다.
     * endRow 는 더 큰 값으로, matchedKeywords 는 중복 없이 합친다.
     */
    public void mergeWith(ExtractBlock other) {
        if (other.endRow > this.endRow) {
            this.endRow = other.endRow;
        }
        for (String kw : other.matchedKeywords) {
            if (!this.matchedKeywords.contains(kw)) {
                this.matchedKeywords.add(kw);
            }
        }
    }

    public int          getStartRow()          { return startRow; }
    public int          getEndRow()            { return endRow; }
    public List<String> getMatchedKeywords()   { return matchedKeywords; }
}
