from datetime import datetime
from operator import itemgetter

from flask import request, jsonify

from backend.config import PROPERTIES_POST, PROPERTIES_COMMAND
from backend.storage.driver import read_from_storage, write_to_storage


def register_routes(app):
    @app.get('/api/v1/posts')
    def get_posts():
        """
        Returns all saved posts from temporary variable POSTS, so keep in mind there's regular resets
        and data loss. Optionally sorts the results by given query params sort and direction.
        No pagination for now.
        :return: The potentially sorted posts.
        """
        # For presentation only
        if request.args.get("debug_error", False):
            return "{[[[[]"

        sort = request.args.get("sort", "id")
        direction = request.args.get("direction", "desc")
        try:
            # page 0 equals page 1 irl
            page = int(request.args.get("page", 0))
            page_size = int(request.args.get("page_size", 10))
        except ValueError:
            page = 0
            page_size = 10

        if page < 0 or page_size <= 0:
            return jsonify({
                "message": 'Invalid page or page_size number. Provide positive integers.'
            }), 422

        pagination_start = page * page_size
        pagination_end = pagination_start + page_size

        if sort not in [*PROPERTIES_POST, "id"]:
            return jsonify({
                "message": 'Invalid sort key.'
            }), 422

        if direction not in ["desc", "asc"]:
            return jsonify({
                "message": 'Invalid direction argument. Provide "desc" or "asc".'
            }), 422

        sorted_posts = sorted(
            read_from_storage(),
            key=itemgetter(sort),
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
            return jsonify(create_error_for_missing_keys(body)), 422

        posts = read_from_storage()

        post = {
            "id": create_id(posts),
            **body,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        write_to_storage([*posts, post])

        return jsonify(post), 201

    @app.get("/api/v1/posts/<int:post_id>")
    def get_single_post(post_id: int):
        """
        Returns a single post as json based on path id.
        """
        post = [
            blog_entry
            for blog_entry in read_from_storage()
            if blog_entry["id"] == post_id
        ][0]

        post_with_comment = {
            **post,
            "comments": list(filter(
                lambda comment: comment.get("post_id") == post.get("id"),
                read_from_storage(data_type="comments")
            ))
        }
        return jsonify(post_with_comment), 200

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
    return {"message": error_msg}


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
