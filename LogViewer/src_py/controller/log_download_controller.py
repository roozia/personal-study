"""
Java 대응: com.logviewer.controller.LogDownloadController

변환 포인트:
    @Controller              →  Blueprint (컨트롤러 묶음 단위)
    @RequestMapping          →  @log_download_bp.route(...)
    HttpServletRequest       →  Flask 전역 request 객체 (파라미터로 받지 않음)
    HttpServletResponse      →  Response 객체를 return으로 반환
"""
from flask import Blueprint, request, Response
from service.log_extract_service import LogExtractService


# ─────────────────────────────────────────────────────────
# Java 대응: @Controller
# Blueprint = Spring MVC Controller의 URL 그룹 단위
# ─────────────────────────────────────────────────────────
log_download_bp = Blueprint('log_download', __name__)

# Java 대응: private final LogExtractService extractService = new LogExtractService();
extract_service = LogExtractService()


# ─────────────────────────────────────────────────────────
# Java 대응:
#   @RequestMapping(value = "/logDownload.do", method = RequestMethod.POST)
#   public void download(HttpServletRequest request, HttpServletResponse response)
# ─────────────────────────────────────────────────────────
@log_download_bp.route('/logDownloadPy.do', methods=['POST'])
def download():
    """
    POST /logDownloadPy.do

    Flask에서 request는 전역 객체로 자동 주입됨
    → Java처럼 파라미터로 받지 않아도 됨

    TODO 1: request.form 에서 파라미터를 추출해 dict로 만드세요
            Java: request.getParameter("filePath")
            Python: request.form.get('filePath', '')

    TODO 2: extract_service.execute(params) 를 호출하세요

    TODO 3: 파일 다운로드 Response를 만들어 return 하세요
            힌트 ↓
            response = Response(content, mimetype='text/plain; charset=utf-8')
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    """
    try:
        # TODO 1: 파라미터 수집
        # 힌트: request.form 은 Java의 request.getParameterMap() 과 유사한 dict-like 객체
      #  params = {
            # 'filePath':          request.form.get('filePath', ''),
            # 'datetimeCondition': request.form.get('datetimeCondition', ''),
            # 'contextLines':      request.form.get('contextLines', ''),
            # 'keywords':          request.form.get('keywords', ''),
       # }

        params = {
            "filePath"          : request.form.get("filePath"),
            "datetimeCondition" : request.form.get("datetimeCondition"),
            "contextLines"      : request.form.get("contextLines"),
            "keywords"          : request.form.get("keywords"),
        }

        # TODO 2: 서비스 호출
        # content, filename = extract_service.execute(params)
        content, filename = extract_service.execute(params) # (2026.06.21) 여러 개의 Return 가능

        # TODO 3: 다운로드 Response 반환
        response = Response(content, mimetype='text/plainl charset=utf-8')
        response.status_code = 200
        response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"'

        return response

        pass

    except Exception as e:
        # Java 대응: sendError(response, e.getMessage())
        # TODO: 에러 응답 반환
        # 힌트: return Response(f'[오류] {str(e)}', status=500, mimetype='text/plain; charset=utf-8')
        return Response(f'[Error] {str(e)}, status=500, mimetype='text/plain; charset=utf-8')
