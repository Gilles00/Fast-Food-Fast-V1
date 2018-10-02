import psycopg2
from functools import wraps
import jwt
from flask import request, make_response
import app.config as config

conn = psycopg2.connect(host="localhost",
                        database=config.DBNAME,
                        user=config.USER,
                        password=config.PASSWORD)


def token_require(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response('Token is missing', 401)
        try:
            data = jwt.decode(token, 'secret_to_encoding', algorithms='HS256')
            user_id = data.get('user_id')
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT user_id, admin FROM Users WHERE user_id = %s", (user_id,))
                    current_user = cur.fetchone()
        except jwt.exceptions.ExpiredSignatureError:
            return make_response("Token has expired Please login again", 401)
        return func(current_user, *args, **kwargs)
    return decorated_func
