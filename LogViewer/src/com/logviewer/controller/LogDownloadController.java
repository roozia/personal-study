package com.logviewer.controller;

import com.logviewer.config.LogViewerConfig;
import com.logviewer.service.LogExtractService;

// ※ Tomcat 버전에 따라 import 패키지를 변경하세요.
//    Tomcat 9  → javax.servlet.*
//    Tomcat 10 → jakarta.servlet.*
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.io.PrintWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * /logDownload.do 요청을 처리하는 컨트롤러.
 *
 * 동작:
 *   1) logviewer.properties 를 읽어 조회 조건 파악
 *   2) LogExtractService 로 로그 파일 발췌
 *   3) 결과를 *.log 파일로 즉시 다운로드 응답
 *
 * 회사 Framework 적용 시 변경 사항:
 *   - @WebServlet 대신 Framework 방식의 URL 매핑으로 교체
 *   - HttpServlet 대신 회사 BaseController 상속으로 교체
 *   - doGet / doPost 대신 Framework 의 action 메서드로 교체
 */
@WebServlet("/logDownload.do")
public class LogDownloadController extends HttpServlet {

    private static final DateTimeFormatter FILENAME_FORMAT =
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

    private final LogExtractService extractService = new LogExtractService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        process(response);
    }

    // 회사 Framework 가 *.do 를 POST 로 호출하는 경우를 위해 doPost 도 위임
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        process(response);
    }

    private void process(HttpServletResponse response) throws IOException {
        try {
            LogViewerConfig config = LogViewerConfig.load();
            String filename = buildFilename(config.getOutputPrefix());

            response.setContentType("text/plain; charset=UTF-8");
            response.setCharacterEncoding("UTF-8");
            response.setHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");

            extractService.extract(config, response.getOutputStream());

        } catch (IOException e) {
            sendError(response, e.getMessage());
        }
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
