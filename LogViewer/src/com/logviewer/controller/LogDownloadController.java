package com.logviewer.controller;

import com.logviewer.config.LogViewerConfig;
import com.logviewer.service.LogExtractService;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import java.io.IOException;
import java.io.PrintWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Controller
public class LogDownloadController {

    private static final DateTimeFormatter FILENAME_FORMAT =
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

    private final LogExtractService extractService = new LogExtractService();

    @RequestMapping(value = "/logDownload.do", method = RequestMethod.POST)
    public void download(HttpServletRequest request, HttpServletResponse response) throws IOException {
        try {
            LogViewerConfig config = LogViewerConfig.load();
            applyRequestParams(request, config);

            String filename = buildFilename(config.getOutputPrefix());
            response.setContentType("text/plain; charset=UTF-8");
            response.setCharacterEncoding("UTF-8");
            response.setHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");

            extractService.extract(config, response.getOutputStream());

        } catch (IOException e) {
            sendError(response, e.getMessage());
        }
    }

    private void applyRequestParams(HttpServletRequest request, LogViewerConfig config) {
        String filePath = trim(request.getParameter("filePath"));
        if (!filePath.isEmpty()) config.setFilePath(filePath);

        String datetimeCondition = trim(request.getParameter("datetimeCondition"));
        if (!datetimeCondition.isEmpty()) config.setDatetimeCondition(datetimeCondition);

        String contextLines = trim(request.getParameter("contextLines"));
        if (!contextLines.isEmpty()) {
            try { config.setContextLines(Integer.parseInt(contextLines)); } catch (NumberFormatException ignored) {}
        }

        String keywords = trim(request.getParameter("keywords"));
        if (!keywords.isEmpty()) config.setKeywords(LogViewerConfig.parseKeywords(keywords));
    }

    private static String trim(String value) {
        return value == null ? "" : value.trim();
    }

    private String buildFilename(String prefix) {
        String timestamp = LocalDateTime.now().format(FILENAME_FORMAT);
        return prefix + "_" + timestamp + ".log";
    }

    private void sendError(HttpServletResponse response, String message) throws IOException {
        response.setContentType("text/plain; charset=UTF-8");
        response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        try (PrintWriter writer = response.getWriter()) {
            writer.write("[오류] " + message);
        }
    }
}
