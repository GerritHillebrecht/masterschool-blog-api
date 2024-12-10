from requests import get

from frontend.config import BASE_URL


def get_all_posts():
    return get(f"{BASE_URL}/posts?sort=id&direction=desc&page_size=6").json()


def get_post(post_id):
    pass
