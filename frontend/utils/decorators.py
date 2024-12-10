from functools import wraps

import requests
from flask import render_template


def handle_request_errors(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as http_err:
            error = {"error": "HTTP error occurred", "message": str(http_err)}
            return render_template("error.html", error=error)
        except requests.exceptions.ConnectionError as conn_err:
            error = {"error": "Connection error occurred", "message": str(conn_err)}
            return render_template("error.html", error=error)
        except requests.exceptions.Timeout as timeout_err:
            error = {"error": "Timeout error occurred", "message": str(timeout_err)}
            return render_template("error.html", error=error)
        except requests.exceptions.RequestException as req_err:
            error = {"error": "Request error occurred", "message": str(req_err)}
            return render_template("error.html", error=error)
        except ValueError as value_err:
            error = {"error": "JSON decode error occurred", "message": str(value_err)}
            return render_template("error.html", error=error)
        except Exception as err:
            error = {"error": "An unexpected error occurred", "message": str(err)}
            return render_template("error.html", error=error)

    return decorated_function
