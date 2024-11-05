POSTS = [
    {**post, "id": index + 1}
    for index, post in enumerate(
        [
            {
                "id": 1,
                "title": "First post",
                "content": "This is the first post.",
                "categories": ["DIY Equipment", "Gardening"],
                "tags": ["garden", "diy", "homemade", "manscaping"]
            },
            {
                "id": 2,
                "title": "Second post",
                "content": "This is the second post.",
                "categories": ["Clothing", "Leather applications"],
                "tags": ["Jacket", "leather", "cloths", "hot&sexy"]
            },
        ] * 30
    )
]

COMMENTS = [
    {"id": 1, "post_id": 1, "author": "John Doe",
     "comment": "What a comment this is. Incredible. Amazing. Astonishing."},
    {"id": 2, "post_id": 1, "author": "John Doe",
     "comment": "What a comment this is. Incredible. Amazing. Astonishing."},
    {"id": 3, "post_id": 1, "author": "John Doe",
     "comment": "What a comment this is. Incredible. Amazing. Astonishing."},
    {"id": 4, "post_id": 2, "author": "Jane Doe", "comment": "Very hateful strange comment. Better ignore it."},
    {"id": 5, "post_id": 2, "author": "Jane Doe", "comment": "Very hateful strange comment. Better ignore it."},
    {"id": 6, "post_id": 2, "author": "Jane Doe", "comment": "Very hateful strange comment. Better ignore it."},
]
