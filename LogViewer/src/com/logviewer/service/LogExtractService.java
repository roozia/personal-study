package com.logviewer.service;

import com.logviewer.config.LogViewerConfig;
import com.logviewer.model.ExtractBlock;
import com.logviewer.model.MatchResult;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

/**
 * 로그 파일에서 조건에 맞는 행을 발췌하여 OutputStream 에 쓴다.
 *
 * 처리 흐름:
 *   Pass 1) 파일을 한 줄씩 읽어 매칭 행 번호 수집 → List<MatchResult>
 *   Build ) MatchResult 목록 → 컨텍스트 적용 → ExtractBlock 목록 → 병합
 *   Pass 2) 파일을 다시 한 줄씩 읽어 블록 범위 행만 출력
 *
 * 파일 전체를 메모리에 올리지 않으므로 대용량 파일도 처리 가능하다.
 */
public class LogExtractService {

    // -------------------------------------------------------------------------
    // 공개 API
    // -------------------------------------------------------------------------

    public void extract(LogViewerConfig config, OutputStream out) throws IOException {
        validatePath(config.getFilePath(), config.getAllowedBaseDir());
        validateCondition(config);

        // Python: list[MatchResult]
        // TS: MatchResult[]
        List<MatchResult> matches = findMatches(config);

        if (matches.isEmpty()) {
            writeText(out, "조건에 매칭되는 로그 라인이 없습니다.\n");
            return;
        }

        List<ExtractBlock> blocks  = buildBlocks(matches, config.getContextLines());
        List<ExtractBlock> merged  = mergeBlocks(blocks);

        writeExtract(config.getFilePath(), config.getFileEncoding(), merged, out);
    }

    // -------------------------------------------------------------------------
    // 검증
    // -------------------------------------------------------------------------

    private void validatePath(String filePath, String allowedBaseDir) throws IOException {
        if (filePath == null || filePath.isEmpty()) {
            throw new IOException("logviewer.file.path 설정이 비어 있습니다.");
        }

        Path normalized = Paths.get(filePath).normalize().toAbsolutePath();

        if (allowedBaseDir != null && !allowedBaseDir.isEmpty()) {
            Path baseDir = Paths.get(allowedBaseDir).normalize().toAbsolutePath();
            if (!normalized.startsWith(baseDir)) {
                throw new IOException("허용되지 않은 경로입니다: " + filePath);
            }
        }

        if (!Files.exists(normalized)) {
            throw new IOException("파일을 찾을 수 없습니다: " + filePath);
        }
        if (!Files.isReadable(normalized)) {
            throw new IOException("파일을 읽을 수 없습니다 (권한 부족): " + filePath);
        }
    }

    private void validateCondition(LogViewerConfig config) throws IOException {
        boolean hasDatetime = !config.getDatetimeCondition().isEmpty();
        boolean hasKeywords = !config.getKeywords().isEmpty();
        if (!hasDatetime && !hasKeywords) {
            throw new IOException(
                "날짜 조건(logviewer.condition.datetime) 또는 " +
                "키워드(logviewer.condition.keywords) 중 하나 이상을 설정해야 합니다.");
        }
    }

    // -------------------------------------------------------------------------
    // Pass 1: 매칭 행 수집
    // -------------------------------------------------------------------------

    private List<MatchResult> findMatches(LogViewerConfig config) throws IOException {
        // Python: list[MatchResult]
        // TS: MatchResult[]
        List<MatchResult> results = new ArrayList<>();
        Charset charset = Charset.forName(config.getFileEncoding());

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(config.getFilePath()), charset))) {

            String line;
            int lineNumber = 0;

            while ((line = reader.readLine()) != null) {
                lineNumber++;
                String matched = matchLine(line, config);
                if (matched != null) {
                    results.add(new MatchResult(lineNumber, matched));
                }
            }
        }

        return results;
    }

    /**
     * 한 줄이 조건에 매칭되면 매칭 키워드를 반환하고, 아니면 null 을 반환한다.
     *
     * 조건 조합 규칙:
     *   - 날짜 + 키워드 설정 시 : 날짜 AND 키워드 (AND)
     *   - 키워드만 설정 시       : 키워드 중 하나라도 포함 (OR)
     *   - 날짜만 설정 시         : 날짜 문자열 포함 여부
     */
    private String matchLine(String line, LogViewerConfig config) {
        boolean hasDatetime = !config.getDatetimeCondition().isEmpty();
        boolean hasKeywords = !config.getKeywords().isEmpty();

        boolean datetimeOk = !hasDatetime || line.contains(config.getDatetimeCondition());

        if (hasKeywords) {
            for (String keyword : config.getKeywords()) {
                if (line.contains(keyword) && datetimeOk) {
                    return keyword;
                }
            }
            return null;
        }

        // 날짜 조건만 있는 경우
        return datetimeOk ? config.getDatetimeCondition() : null;
    }

    // -------------------------------------------------------------------------
    // 블록 구성 및 병합
    // -------------------------------------------------------------------------

    private List<ExtractBlock> buildBlocks(List<MatchResult> matches, int contextLines) {
        // Python: list[ExtractBlock]
        // TS: ExtractBlock[]
        List<ExtractBlock> blocks = new ArrayList<>();

        for (MatchResult match : matches) {
            int start = Math.max(1, match.getLineNumber() - contextLines);
            int end   = match.getLineNumber() + contextLines;

            List<String> keywords = new ArrayList<>();
            keywords.add(match.getMatchedKeyword());

            blocks.add(new ExtractBlock(start, end, keywords));
        }

        return blocks;
    }

    /**
     * 겹치거나 인접한 블록을 하나로 합친다.
     * 입력 블록은 startRow 오름차순(findMatches 의 순서 보장)임을 가정한다.
     */
    private List<ExtractBlock> mergeBlocks(List<ExtractBlock> blocks) {
        // Python: list[ExtractBlock]
        // TS: ExtractBlock[]
        List<ExtractBlock> merged = new ArrayList<>();

        for (ExtractBlock current : blocks) {
            if (merged.isEmpty()) {
                merged.add(current);
                continue;
            }

            ExtractBlock last = merged.get(merged.size() - 1);
            if (last.overlapsOrAdjacent(current)) {
                last.mergeWith(current);
            } else {
                merged.add(current);
            }
        }

        return merged;
    }

    // -------------------------------------------------------------------------
    // Pass 2: 발췌 내용 출력
    // -------------------------------------------------------------------------

    private void writeExtract(String filePath, String fileEncoding,
                               List<ExtractBlock> blocks, OutputStream out) throws IOException {
        Charset inputCharset = Charset.forName(fileEncoding);

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(filePath), inputCharset));
             PrintWriter writer = new PrintWriter(
                new OutputStreamWriter(out, "UTF-8"), false)) {

            int currentLine = 0;

            for (ExtractBlock block : blocks) {
                // 블록 시작 전까지 건너뛴다
                while (currentLine < block.getStartRow() - 1) {
                    if (reader.readLine() == null) {
                        writer.flush();
                        return;
                    }
                    currentLine++;
                }

                writer.println(buildHeader(block));

                // 블록 범위 행 출력
                while (currentLine < block.getEndRow()) {
                    String line = reader.readLine();
                    if (line == null) break;
                    currentLine++;
                    writer.println(line);
                }

                writer.println();
            }

            writer.flush();
        }
    }

    // -------------------------------------------------------------------------
    // 유틸
    // -------------------------------------------------------------------------

    private String buildHeader(ExtractBlock block) {
        StringBuilder sb = new StringBuilder("========== [Row: ");
        sb.append(block.getStartRow()).append("-").append(block.getEndRow());
        sb.append(" / Keyword: ");

        List<String> keywords = block.getMatchedKeywords();
        for (int i = 0; i < keywords.size(); i++) {
            if (i > 0) sb.append(", ");
            sb.append('"').append(keywords.get(i)).append('"');
        }

        sb.append("] ==========");
        return sb.toString();
    }

    private void writeText(OutputStream out, String text) throws IOException {
        try (PrintWriter writer = new PrintWriter(new OutputStreamWriter(out, "UTF-8"))) {
            writer.print(text);
            writer.flush();
        }
    }
}
