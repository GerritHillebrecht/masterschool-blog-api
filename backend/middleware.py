from flask import Response

from backend.middlewares.ratelimiter import RateLimiter


class RateLimitingMiddleware:
    def __init__(self, app):
        self.app = app
        self.rateLimiter = RateLimiter(max_tokens=100, rate=50)

    def __call__(self, environ, start_response):
        if self.rateLimiter.request_token():
            response = self.app(environ, start_response)
            return response

        res = Response('Rate limit exceeded. Try again later.', status=429)
        return res(environ, start_response)
