import json
import sqlite3
import datetime
from .utils import JSON_MIME_TYPE

from flask import Flask, Response, abort
from flask import g

app = Flask(__name__)


def connect_db(db_name):
    return sqlite3.connect(db_name)


@app.before_request
def before_request():
    g.db = connect_db(app.config['DATABASE'])


@app.route("/tweet/<int:TWEET_ID>")
def get_tweety(TWEET_ID):
    g.db.row_factory = sqlite3.Row
    query = """
    SELECT t.id as id, u.username as profile,
    t.created as date, t.content as content FROM
    tweet t NATURAL INNER JOIN user u
    WHERE t.id == '{}'
    """
    tweet_cursor = g.db.execute(query.format(TWEET_ID))
    # This will return None if the 0 items in the query
    tweet_fetch = tweet_cursor.fetchone()

    if not tweet_fetch:
        abort(404)
    tweet_dict = dict(zip(tweet_fetch.keys(), tuple(tweet_fetch)))

    tweet_dict['uri'] = '/tweet/{}'.format(TWEET_ID)
    tweet_dict['profile'] = '/profile/{}'.format(tweet_dict['profile'])
    time = datetime.datetime.strptime(tweet_dict['date'], '%Y-%m-%d %H:%M:%S')
    tweet_dict['date'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    tweet_json = json.dumps(tweet_dict)
    return tweet_json, 200, {'Content-Type': JSON_MIME_TYPE}


@app.route("/profile/<username>")
def get_profile(username):
    query = """
    SELECT u.id as user_id, u.username as username,
    u.first_name as first_name, u.last_name as last_name,
    u.birth_date as birth_date FROM user u WHERE u.username == '{}'
    """
    g.db.row_factory = sqlite3.Row
    profile_cursor = g.db.execute(query.format(username))
    profile_fetch = profile_cursor.fetchone()
    if not profile_fetch:
        abort(404)
    profile_dict = dict(profile_fetch)
    profile_dict['tweet_count'] = 0
    tweet_query = """
    SELECT t.created as date, t.id as id, t.content as text
    FROM tweet t NATURAL JOIN user WHERE t.user_id = '{}'
    """
    tweets_cursor = g.db.execute(tweet_query.format(profile_dict['user_id']))
    tweet_fetch = [dict(tweet) for tweet in tweets_cursor.fetchall()]
    for tweet_dict in tweet_fetch:
        profile_dict['tweet_count'] += 1
        tweet_dict['uri'] = '/tweet/{}'.format(tweet_dict['id'])
        time = datetime.datetime.strptime(tweet_dict['date'],
                                          '%Y-%m-%d %H:%M:%S')
        tweet_dict['date'] = time.strftime('%Y-%m-%dT%H:%M:%S')

    profile_dict['tweets'] = tweet_fetch

    print(profile_dict)
    profile_json = json.dumps(profile_dict)
    return profile_json, 200, {'Content-Type': JSON_MIME_TYPE}


@app.route("/login", methods=['POST'])
def login():
    pass


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
