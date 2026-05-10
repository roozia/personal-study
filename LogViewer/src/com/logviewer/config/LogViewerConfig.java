package com.logviewer.config;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

/**
 * logviewer.properties 를 읽어 설정값을 보관하는 DTO.
 *
 * 로딩 우선순위:
 *   1) JVM 시스템 속성 -Dlogviewer.config.path=/경로/logviewer.properties (재시작 없이 변경 가능)
 *   2) 클래스패스 루트의 /logviewer.properties (WEB-INF/classes/)
 */
public class LogViewerConfig {

    private static final String SYSTEM_PROPERTY_KEY = "logviewer.config.path";
    private static final String CLASSPATH_DEFAULT    = "/logviewer.properties";

    private String filePath;
    private String fileEncoding;
    private String datetimeCondition;
    // Python: list[str]
    // TS: string[]
    private List<String> keywords;
    private int    contextLines;
    private String outputPrefix;
    private String allowedBaseDir;

    // -------------------------------------------------------------------------
    // 생성자 / 팩토리
    // -------------------------------------------------------------------------

    private LogViewerConfig() {}

    public static LogViewerConfig load() throws IOException {
        Properties props = readProperties();

        LogViewerConfig cfg = new LogViewerConfig();
        cfg.filePath          = props.getProperty("logviewer.file.path",          "").trim();
        cfg.fileEncoding      = props.getProperty("logviewer.file.encoding",      "UTF-8").trim();
        cfg.datetimeCondition = props.getProperty("logviewer.condition.datetime", "").trim();
        cfg.contextLines      = parseContextLines(props.getProperty("logviewer.context.lines", "10"));
        cfg.outputPrefix      = props.getProperty("logviewer.output.prefix",      "extract").trim();
        cfg.allowedBaseDir    = props.getProperty("logviewer.allowed.basedir",    "").trim();
        cfg.keywords          = parseKeywords(props.getProperty("logviewer.condition.keywords", ""));
        return cfg;
    }

    // -------------------------------------------------------------------------
    // 내부 파싱 유틸
    // -------------------------------------------------------------------------

    private static Properties readProperties() throws IOException {
        Properties props = new Properties();
        String externalPath = System.getProperty(SYSTEM_PROPERTY_KEY);

        if (externalPath != null && !externalPath.isEmpty()) {
            try (InputStream in = new FileInputStream(externalPath)) {
                props.load(in);
            }
        } else {
            try (InputStream in = LogViewerConfig.class.getResourceAsStream(CLASSPATH_DEFAULT)) {
                if (in == null) {
                    throw new IOException("설정 파일을 찾을 수 없습니다. 클래스패스: " + CLASSPATH_DEFAULT
                            + "  또는 -D" + SYSTEM_PROPERTY_KEY + "=<경로> 로 지정하세요.");
                }
                props.load(in);
            }
        }
        return props;
    }

    public static List<String> parseKeywords(String raw) {
        // Python: list[str]
        // TS: string[]
        List<String> result = new ArrayList<>();
        if (raw == null || raw.trim().isEmpty()) {
            return result;
        }
        for (String kw : raw.split(",")) {
            String trimmed = kw.trim();
            if (!trimmed.isEmpty()) {
                result.add(trimmed);
            }
        }
        return result;
    }

    private static int parseContextLines(String value) {
        try {
            int n = Integer.parseInt(value.trim());
            return Math.max(0, n);
        } catch (NumberFormatException e) {
            return 10;
        }
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    public String       getFilePath()          { return filePath; }
    public String       getFileEncoding()      { return fileEncoding; }
    public String       getDatetimeCondition() { return datetimeCondition; }
    public List<String> getKeywords()          { return keywords; }
    public int          getContextLines()      { return contextLines; }
    public String       getOutputPrefix()      { return outputPrefix; }
    public String       getAllowedBaseDir()     { return allowedBaseDir; }

    // -------------------------------------------------------------------------
    // Setters (화면 입력값으로 properties 기본값 override 시 사용)
    // -------------------------------------------------------------------------

    public void setFilePath(String filePath)                   { this.filePath = filePath; }
    public void setDatetimeCondition(String datetimeCondition) { this.datetimeCondition = datetimeCondition; }
    public void setContextLines(int contextLines)              { this.contextLines = contextLines; }
    public void setKeywords(List<String> keywords)             { this.keywords = keywords; }
}
