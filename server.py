import flask
from flask import Flask, request
from database import create_client, query_news, query_keywords

app = Flask(__name__)


@app.route("/")
def news():
    return ""


@app.route("/get_news")
def get_news():
    text = request.args.get("text")
    keywords = request.args.to_dict(flat=False).get("keywords")
    limit_str = request.args.get("limit")
    try:
        if limit_str is None:
            limit = None
        else:
            limit = int(limit_str)
            if limit < 0:
                raise ValueError
        if limit is None or limit > 100:
            limit = 100
        with create_client() as client:
            res = query_news(client, text, keywords, limit)
        return {"news": res}
    except ValueError:
        flask.abort(400)


@app.route("/get_keywords")
def get_keywords():
    with create_client() as client:
        res = query_keywords(client)
    return {"keywords": res}
