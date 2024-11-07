"""
There's no authorization for now. Having users saved in a database but not the posts & comments feels weird.
Also takes up at least as much time as the main task. Gonna add authorization to apps when databases are
handled.
Also no likes. Adding extra swagger documentation for a new add-like route is too much work for such a little
feature.
"""

from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from middleware import RateLimitingMiddleware
from storage.driver import read_from_storage, write_to_storage

app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/masterblog.json"  # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'  # (3) You can change this if you like
    }
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
app.wsgi_app = RateLimitingMiddleware(app.wsgi_app)

PROPERTIES_POST = ("title", "content", "categories", "tags", "author")
PROPERTIES_COMMAND = ("post_id", "author", "title", "comment")


@app.get('/api/v1/posts')
def get_posts():
    """
    Returns all saved posts from temporary variable POSTS, so keep in mind there's regular resets
    and data loss. Optionally sorts the results by given query params sort and direction.
    No pagination for now.
    :return: The potentially sorted posts.
    """
    sort = request.args.get("sort", "id")
    direction = request.args.get("direction", "desc")
    page = int(request.args.get("page", 0))
    page_size = int(request.args.get("page_size", 10))

    pagination_start = page * page_size
    pagination_end = pagination_start + page_size

    if sort not in [*PROPERTIES_POST, "id"]:
        return jsonify({
            "message": f'Invalid sort key.'
        }), 422

    if direction not in ["desc", "asc"]:
        return jsonify({
            "message": f'Invalid direction argument. Provide "desc" or "asc".'
        }), 422

    sorted_posts = sorted(
        read_from_storage(),
        key=lambda post: post.get(sort),
        reverse=direction == "desc"
    )

    paginated_posts = sorted_posts[pagination_start:pagination_end]

    posts_with_comments = map(
        lambda post: {
            **post,
            "comments": list(filter(
                lambda comment: comment.get("post_id") == post.get("id"),
                read_from_storage(data_type="comments")
            ))
        },
        paginated_posts
    )

    return jsonify(list(
        posts_with_comments
    ))


@app.post('/api/v1/posts')
def add_post():
    """
    Takes in JSON body to add a post to the storage.
    :return: The added post including the generated id.
    """
    body = request.get_json()

    if not validate_request_body(body):
        return create_error_for_missing_keys(body)

    posts = read_from_storage()

    post = {
        "id": create_id(posts),
        **body,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    write_to_storage([*posts, post])

    return jsonify(post), 201


@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id: int):
    """
    Removes the post with the given post_id from the storage.
    :param post_id: The id of the post to delete.
    :return: A message object.
    """
    posts = read_from_storage()
    comments = read_from_storage(data_type="comments")

    if not post_id or post_id not in [p.get("id") for p in posts]:
        return jsonify({
            "message": f'Post with id <{post_id}> not found.'
        }), 404

    # Delete Post
    write_to_storage([
        post
        for post in posts
        if post.get("id") != post_id
    ])

    # Delete comments of that post
    write_to_storage([
        comment
        for comment in comments
        if comment.get("post_id") != post_id
    ], data_type="comments")

    return jsonify({
        "message": f"Post with id <{post_id}> has been deleted successfully."
    }), 200


@app.put("/api/v1/posts/<int:post_id>")
def update_post(post_id: int):
    """
    Updates a post based on the path-id and the provided json body.
    :param post_id: The id passed according to the path.
    :return: Returns the updated post.
    """
    posts = read_from_storage()

    try:
        idx = [p.get("id") for p in posts].index(post_id)
    except ValueError:
        return jsonify({
            "message": f'Post with id <{post_id}> not found.'
        }), 404

    body = request.get_json()

    if not isinstance(body, dict):
        return jsonify({
            "message": f'Please provide post-data as json object.'
        }), 422

    posts[idx] = {
        **posts[idx],
        **body,
        "updated_at": datetime.now()
    }

    write_to_storage(posts)

    return posts[idx], 200


@app.get("/api/v1/posts/search")
def search_posts():
    """
    Filters posts by given title and content arguments passed via query params.
    :return: Filtered posts.
    """
    search_title = request.args.get("title", "").lower()
    search_content = request.args.get("content", "").lower()

    return jsonify(list(filter(
        lambda post: search_title in post.get("title").lower() and search_content in post.get("content").lower(),
        read_from_storage()
    ))), 200


@app.get("/api/v1/comments")
def get_comments():
    """
    Returns all comments.
    """
    return jsonify(list(map(
        format_dates,
        read_from_storage(data_type="comments")
    )))


@app.post("/api/v1/comments")
def add_comment():
    """
    Creates a comment based on the request body data.
    :return: The created comment.
    """
    body = request.get_json()

    if not validate_request_body(body, keys=PROPERTIES_COMMAND):
        return create_error_for_missing_keys(body, keys=PROPERTIES_COMMAND)

    comments = read_from_storage(data_type="comments")

    comment = {
        **body,
        "id": create_id(comments),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    write_to_storage([*comments, comment], data_type="comments")

    return jsonify(format_dates(comment))


@app.get("/api/v1/comments/<int:post_id>")
def get_specific_comments(post_id: int):
    """
    Returns all comments of a specific post.
    :param post_id: The id of the post.
    :return: All comments belonging to that post.
    """
    return jsonify(list(
        filter(
            lambda comment: comment.get("post_id") == post_id,
            map(
                format_dates,
                read_from_storage(data_type="comments")
            )
        )
    ))


@app.delete("/api/v1/comments/<int:comment_id>")
def delete_comment(comment_id: int):
    """
    Deletes a comment by id.
    :param comment_id: Id provided by the path.
    """
    comments = read_from_storage(data_type="comments")

    if comment_id not in [c.get("id") for c in comments]:
        return jsonify({
            "message": f'Comment with id <{comment_id}> not found.'
        }), 404

    write_to_storage(list(filter(
        lambda comment: comment.get("id") != comment_id,
        comments
    )))

    return jsonify({
        "message": f"Comment with id <{comment_id}> has been deleted successfully."
    }), 200


def validate_request_body(body, keys=PROPERTIES_POST):
    """
    Pre-checks request body for validity and completeness. No sanity checks.
    :param body: The request body.
    :param keys: The keys that the body has to be checked against.
    :return: Boolean value for whether the post can be created based on the given data.
    """
    return isinstance(body, dict) and all(key in body for key in keys)


def create_error_for_missing_keys(body, keys=PROPERTIES_POST):
    """
    Creates a missing data error message and combines it with the correct error-code 422.
    :param body: The json data submitted by the request.
    :param keys: The required keys to check against.
    :return: A tuple with the error msg and the error code.
    """
    error_msg = " and ".join(
        filter(
            lambda err: err,
            (
                f'missing data for: "{key}"' if key not in body else False
                for key in keys
            )
        )

    )
    return {"message": error_msg}, 422


def create_id(items) -> int:
    """
    Creates an id based on the already used ids in items. Always one-ups the currently highest id.
    :param items: The list of items with ids that needs a new id.
    :return: A new id.
    """
    return max([item["id"] for item in items], default=0) + 1


def format_dates(item: dict) -> dict:
    """
    Formats items for the front-end. Replaces date-objects with iso-dates.
    :param item: Item holding "created_at" and "updated_at" date-objects.
    :return: Item with iso-dates.
    """
    return {
        **item,
        "created_at": item.get("created_at").isoformat(),
        "updated_at": item.get("updated_at").isoformat()
    }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
