from flask import render_template
from requests import get

from frontend.config import BASE_URL
from frontend.utils.decorators import handle_request_errors

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Pen & Pixel API"}
)


def register_routes(app):
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.get('/ms')
    def home():
        return render_template("index.html")

    @app.get("/")
    @handle_request_errors
    def start():
        # Simulate Error
        # posts = get(f"{BASE_URL}/posts?sort=id&direction=desc&page_size=6&debug_error=True")
        posts = get(f"{BASE_URL}/posts?sort=id&direction=desc&page_size=6")
        posts = posts.json()
        print("posts:", posts)
        return render_template("home.html", posts=posts)

    # TODO: VALIDATE GET & JSON
    @app.get("/blog/<int:blog_entry_id>")
    @handle_request_errors
    def view_blog_entry(blog_entry_id: int):
        post = get(f"http://localhost:5002/api/v1/posts/{blog_entry_id}")
        post = post.json()

        return render_template("view_blog_post.html", **post)

    @app.get(f'/docs')
    def custom_swagger_ui():
        return render_template('swagger_ui_with_navbar.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
