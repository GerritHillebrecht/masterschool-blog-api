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
def get_posts() -> list[dict]:
    """
    Returns all saved posts from temporary variable POSTS, so keep in mind there's regular resets
    and data loss. Optionally sorts the results by given query params sort and direction.
    No pagination for now.
    :return: The potentially sorted posts.
    """
    # Usually I'd go with the default-values "id" and "asc" for sort and direction
    # but the assignment specifically wants it to be FiFo, so no alteration.
    sort = request.args.get("sort")
    direction = request.args.get("direction")

    if not sort or not direction:
        return jsonify(POSTS), 200

    if sort not in POST_DATA:
        return jsonify({
            "message": f'Invalid sort key.'
        }), 422

    if direction not in ["desc", "asc"]:
        return jsonify({
            "message": f'Invalid direction argument. Provide "desc" or "asc".'
        }), 422

    return jsonify(list(
        sorted(
            POSTS,
            key=lambda post: post.get(sort),
            reverse=direction == "desc"
        )
    ))


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

    post = {
        "id": max([p.get("id", 0) for p in POSTS], default=0) + 1,
        "title": title,
        "content": content
    }

    POSTS.append(post)

    return jsonify(post), 201


@app.delete("/api/posts/<int:post_id>")
def delete_post(post_id: int):
    global POSTS
    if not post_id or post_id not in [p.get("id") for p in POSTS]:
        return jsonify({
            "message": f'Post with id <{post_id}> not found.'
        }), 404

    POSTS = [
        post
        for post in POSTS
        if post.get("id") != post_id
    ]

    return jsonify({
        "message": f"Post with id <{post_id}> has been deleted successfully."
    }), 200


@app.put("/api/posts/<int:post_id>")
def update_post(post_id: int):
    try:
        idx = [p.get("id") for p in POSTS].index(post_id)
    except ValueError:
        return jsonify({
            "message": f'Post with id <{post_id}> not found.'
        }), 404

    body = request.get_json()

    if not isinstance(body, dict):
        return jsonify({
            "message": f'Please provide data as json object.'
        }), 422

    POSTS[idx] = {
        **POSTS[idx],
        **body
    }

    return POSTS[idx], 200


@app.get("/api/posts/search")
def search_posts():
    search_title = request.args.get("title", "").lower()
    search_content = request.args.get("content", "").lower()

    return jsonify(list(filter(
        lambda post: search_title in post.get("title").lower() and search_content in post.get("content").lower(),
        POSTS
    ))), 200


def validate_post_data(body):
    return isinstance(body, dict) and all(key in body for key in POST_DATA)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
