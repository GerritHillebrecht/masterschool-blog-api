from datetime import datetime

from flask import Flask, request

from frontend.routes.frontend_routes import register_routes
from flask_cors import CORS


def create_app():
    flask_app = Flask(__name__)
    CORS(flask_app)

    @flask_app.context_processor
    def inject_current_path():
        return {'current_path': request.path}

    @flask_app.context_processor
    def inject_title():
        return {'app_title': "Pen & Pixels"}

    @flask_app.template_filter('format_date')
    def format_date(value, format='%d. %B %Y'):
        date = datetime.strptime(value, '%a, %d %b %Y %H:%M:%S %Z')
        return date.strftime(format)

    register_routes(flask_app)

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
