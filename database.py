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


def delete_db(client):
    client.drop_database(DATABASE_NAME)


def delete_content(client):
    db = client.get_database(DATABASE_NAME)
    db.news.delete_many({})


def create_client():
    return pymongo.MongoClient(DATABASE_URL, DATABASE_PORT)


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
