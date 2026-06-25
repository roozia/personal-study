"""
LogViewer Python 버전 - Flask 웹 애플리케이션 진입점

Java 대응 관계:
    web.xml                  →  Flask 앱 생성 + Blueprint 등록
    dispatcher-servlet.xml   →  Blueprint URL 매핑n
    Tomcat 서버              →  Flask 내장 개발 서버 (app.run)

실행 방법:
    1) pip install -r requirements.txt
    2) python app.py
    3) 브라우저에서 http://localhost:8080/logDownloadPy.html 접속
"""
from flask import Flask, render_template
from controller.log_download_controller import log_download_bp

# ─────────────────────────────────────────────────────────
# Java 대응: ApplicationContext / DispatcherServlet 초기화
# ────────────────────────────────────────────ccccc─────────────
app = Flask(__name__)

# ─────────────────────────────────────────────────────────
# Java 대응: @Controller 컴포넌트 스캔 / URL 매핑 등록
# Blueprint = Spring의 @Controller 묶음 단위
# ─────────────────────────────────────────────────────────
app.register_blueprint(log_download_bp)


# ─────────────────────────────────────────────────────────
# HTML 페이지 서빙
# Java: Tomcat이 web/ 폴더의 정적 HTML을 직접 서빙
# Python: Flask가 templates/ 폴더에서 HTML을 렌더링
# ─────────────────────────────────────────────────────────
@app.route('/logDownloadPy.html')
def index():
    return render_template('logDownloadPy.html')


if __name__ == '__main__':
    # Java 대응: Tomcat 서버 시작
    # debug=True → 소스 변경 시 자동 재시작 (개발용)
    app.run(host='0.0.0.0', port=8080, debug=True)
