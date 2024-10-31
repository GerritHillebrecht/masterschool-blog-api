from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POST_DATA = ("title", "content")

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.get('/api/posts')
def get_posts():
    return jsonify(POSTS)


@app.post('/api/posts')
def add_post():
    body = request.get_json()

    if not validate_post_data(body):
        error_msg = " and ".join(
            filter(
                lambda err: err,
                (
                    f'Missing data for: "{key}"' if key not in body else False
                    for key in POST_DATA
                )
            )

        )
        return error_msg, 422

    title, content, *rest = body.values()

    global POSTS
    post = {
        "id": max(p.get("id", 0) for p in POSTS) + 1,
        "title": title,
        "content": content
    }

    POSTS.append(post)

    return jsonify(post), 201


def validate_post_data(body):
    return isinstance(body, dict) and all(key in body for key in POST_DATA)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)