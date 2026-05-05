package com.logviewer.model;

/**
 * Pass 1 에서 발견된 매칭 라인 하나를 나타내는 객체.
 * lineNumber : 원본 파일 기준 1-based 줄 번호
 * matchedKeyword : 해당 라인을 매칭시킨 키워드 (날짜 조건 단독 매칭 시에는 날짜 문자열)
 */
public class MatchResult {

    private final int    lineNumber;
    private final String matchedKeyword;

    public MatchResult(int lineNumber, String matchedKeyword) {
        this.lineNumber     = lineNumber;
        this.matchedKeyword = matchedKeyword;
    }

    // Python: int
    // TS: number
    public int    getLineNumber()       { return lineNumber; }
    // Python: str
    // TS: string
    public String getMatchedKeyword()   { return matchedKeyword; }
}
