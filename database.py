import argparse
import pymongo
from config import (
    DATABASE_URL,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USERNAME,
    DATABASE_PASSWORD_FILE,
)


def init_db(client):
    """Initialize database.

    Args:
        client (pymongo.MongoClient): A client for connecting to the specified database.
    """
    db = client.get_database(DATABASE_NAME)
    db.news.create_index([("url", pymongo.ASCENDING),], unique=True)
    db.news.create_index([("publication_date", pymongo.ASCENDING)])
    db.news.create_index([("title", pymongo.ASCENDING)])
    db.news.create_index([("article", pymongo.TEXT),], default_language="english")
    db.news.create_index([("keywords", pymongo.ASCENDING)])


def insert_news(client, data):
    """Insert news into database.

    Args:
        client (pymongo.MongoClient): A client for connecting to the specified database.
        data (dict): News dict with the following keys:
          - url: Url of the news article
          - publication_date: Publication date of the article
          - title: Title of the article
          - keywords: List of keywords of the article
    """
    db = client.get_database(DATABASE_NAME)
    db.news.update({"url": data["url"]}, data, upsert=True)


def query_news(client, text_query, keyword_list, limit):
    """Query news by keywords and/ or keywords.

    Args:
        client (pymongo.MongoClient): A client for connecting to the specified database.
        text_query (str): Text for querying article body.
        keyword_list (list(str)): List of keywords, where the article must match all of them.
        limit (int): Article limit.

    Raises:
        ValueError: Raised when there is an error in parameter.

    Returns:
        list(dict): List of news matching the query.
    """
    db = client.get_database(DATABASE_NAME)
    query = {}
    if text_query is not None:
        if not isinstance(text_query, str):
            raise ValueError
        query["$text"] = {"$search": text_query}
    if keyword_list is not None:
        if not isinstance(keyword_list, list) or any(
            not isinstance(keyword, str) for keyword in keyword_list
        ):
            raise ValueError
        query["keywords"] = {"$all": keyword_list}
    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise ValueError
    cursor = db.news.find(query, {"_id": 0, "score": {"$meta": "textScore"}})
    cursor = cursor.sort([("score", {"$meta": "textScore"})])
    cursor = cursor.limit(limit)
    return list(cursor)


def query_keywords(client):
    """Query list of keywords in database.

    Args:
        client (pymongo.MongoClient): A client for connecting to the specified database.

    Returns:
        list(str): List of keywords.
    """
    db = client.get_database(DATABASE_NAME)
    return db.news.distinct("keywords", {"keywords": {"$ne": []}})


def delete_db(client):
    """Drop the specified database. All data and indices will be deleted.

    Args:
        client (pymongo.MongoClient): A client for connecting to the specified database.
    """
    client.drop_database(DATABASE_NAME)


def delete_content(client):
    """Delete all data of the specified database. Collection indices are kept.

    Args:
        client (pymongo.MongoClient): A client for connecting to the specified database.
    """
    db = client.get_database(DATABASE_NAME)
    db.news.delete_many({})


def create_client():
    """Create database client.

    Returns:
        pymongo.MongoClient: A client for connecting to the specified database.
    """
    with open(DATABASE_PASSWORD_FILE, "r") as f:
        password = f.read()
    return pymongo.MongoClient(
        DATABASE_URL,
        DATABASE_PORT,
        username=DATABASE_USERNAME,
        password=password,
        tls=True,
    )


def destroy_client(client):
    """Destroy database client by closing active connections to database.

    Args:
        client (pymongo.MongoClient): The database client to be destroyed.
    """
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database Management.")
    parser.add_argument("action", choices=["init_db", "delete_content", "delete_db"])
    args = parser.parse_args()

    with create_client() as client:
        if args.action == "init_db":
            init_db(client)
        elif args.action == "delete_content":
            delete_content(client)
        elif args.action == "delete_db":
            delete_db(client)
