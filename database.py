import pymongo
import argparse
from config import DATABASE_URL, DATABASE_PORT, DATABASE_NAME


def init_db(client):
    db = client.get_database(DATABASE_NAME)
    db.news.create_index([("url", pymongo.ASCENDING),], unique=True)
    db.news.create_index([("publication_date", pymongo.ASCENDING)])
    db.news.create_index([("title", pymongo.ASCENDING)])
    db.news.create_index([("article", pymongo.TEXT),], default_language="english")
    db.news.create_index([("keywords", pymongo.ASCENDING)])


def insert_news(client, data):
    db = client.get_database(DATABASE_NAME)
    db.news.update({"url": data["url"]}, data, upsert=True)


def query_news(client, text_query, keyword_list, limit):
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
        query["keywords"] = {"$in": keyword_list}
    if limit is not None:
        if not isinstance(limit, int) or limit < 0:
            raise ValueError
    cursor = db.news.find(query, {"_id": 0, "score": {"$meta": "textScore"}})
    cursor = cursor.sort([("score", {"$meta": "textScore"})])
    cursor = cursor.limit(limit)
    return list(cursor)


def query_keywords(client):
    db = client.get_database(DATABASE_NAME)
    return db.news.distinct("keywords", {"keywords": {"$ne": []}})


def delete_db(client):
    client.drop_database(DATABASE_NAME)


def delete_content(client):
    db = client.get_database(DATABASE_NAME)
    db.news.delete_many({})


def create_client():
    return pymongo.MongoClient(DATABASE_URL, DATABASE_PORT)


def destroy_client(client):
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
