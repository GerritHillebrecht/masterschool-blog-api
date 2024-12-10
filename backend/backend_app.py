"""
There's no authorization for now. Having users saved in a database but not the posts & comments feels weird.
Also takes up at least as much time as the main task. Going to add authorization to apps when databases are
handled.
Also no likes. Adding extra swagger documentation for a new add-like route is too much work for such a little
feature.
"""

from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from backend.middleware import RateLimitingMiddleware
from backend.routes.api_routes import register_routes

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Pen & Pixl'
    }
)


def create_app():
    flask_app = Flask(__name__)
    CORS(flask_app)

    flask_app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    # No Ratelimiter during development
    # flask_app.wsgi_app = RateLimitingMiddleware(flask_app.wsgi_app)
    register_routes(flask_app)

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5002, debug=True)
