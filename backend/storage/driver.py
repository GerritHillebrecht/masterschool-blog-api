from json import dumps, loads, JSONDecodeError
from datetime import datetime
from os import path, getcwd

# The supported data types. For now, posts and comments.
BASE_URL = "storage"
TYPES = {
    "posts": path.join(getcwd(), BASE_URL, "posts.json"),
    "comments": path.join(getcwd(), BASE_URL, "comments.json")
}

# Make sure all storage files exit
for path in TYPES:
    if not path.find(path):
        open(path, "x")


def read_from_storage(data_type="posts") -> list[dict]:
    """
    Reads data from JSON storage.
    :param data_type: Optional. The type of data needed. Usually posts or comments.
    :return: A list of all requested items.
    """
    if data_type not in TYPES:
        raise TypeError("Provide a supported Datatype")

    with open(TYPES[data_type], "r") as handle:
        try:
            loaded_data = loads(handle.read())
        except JSONDecodeError:
            print("""
            File is corrupted. Everything is lost. No backups.
            Just start from the beginning and never speak of this again.
            """)
            return []

        return list(map(
            parse_item,
            loaded_data
        ))


def write_to_storage(content: list[dict], data_type="posts"):
    """
    Stores provided data in the selected JSON storage.
    :param content: The content to be saved. Usually a list of posts or comments.
    :param data_type: Optional. The type of data needed. Usually posts or comments.
    """
    if data_type not in TYPES:
        raise TypeError("Provide a supported Datatype")

    with open(TYPES[data_type], "w") as handle:
        return handle.write(dumps(list(map(
            format_item,
            content
        ))))


def format_item(item: dict):
    """
    Formats items dates.
    :param item: Object that has "created_at" and "updated_at" date objects.
    :return: The same dictionary with updated "created_at" and "updated_at" values.
    """

    validate_item(item)

    return {
        **item,
        "created_at": format_iso_date(item.get("created_at")),
        "updated_at": format_iso_date(item.get("updated_at"))
    }


def parse_item(item: dict):
    """
    Parses an item to provide parsed date-objects.
    :param item: An item with "created_at" and "updated_at" values to update.
    :return: The updated item.
    """

    validate_item(item)

    return {
        **item,
        "created_at": parse_iso_date(item.get("created_at")),
        "updated_at": parse_iso_date(item.get("updated_at"))
    }


def parse_iso_date(isodate: str):
    """
    Parses an iso-datestring.
    :param isodate: The date formated as iso-string.
    :return: A date-object.
    """
    return datetime.fromisoformat(isodate)


def format_iso_date(date_object):
    """
    Formats a date into an iso-string.
    :param date_object: A date object.
    :return: An iso-string.
    """
    return date_object.isoformat()


def validate_item(item: dict):
    if "created_at" not in item or "updated_at" not in item:
        raise ValueError("Provide a valid item.")
