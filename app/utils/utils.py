import jwt
from time import time
from .environment import CKEDITOR_COLLAB_ACCESS_KEY, CKEDITOR_COLLAB_ENV_ID, CKEDITOR_COLLAB_API_SECRET
import bcrypt
import hmac
import hashlib
import json
import urllib.parse
from typing import Optional
import logging
import sys

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    return logger

def hmacDigest(data:str, key:str):
    keyEncoded = key.encode()
    dataEncoded = data.encode()

    h = hmac.new(keyEncoded, dataEncoded, hashlib.sha256)

    return h.hexdigest()


def generateSignature(method:str , uri:str, timestamp, body: Optional[str]):
    url = urllib.parse.urlparse(uri)
    path = url.path
    if (url.query):
        path = path + "?" + url.query

    methodUpperCase = method.upper()
    data = methodUpperCase + path + str(timestamp)

    if (body):
        data += json.dumps(body, separators=(',',':'))

    return hmacDigest(data, CKEDITOR_COLLAB_API_SECRET)

def generate_collab_token():
    timestamp = int(time())
    
    payload = {
        'aud': CKEDITOR_COLLAB_ENV_ID,
        'iat': timestamp,
        'sub': 'user-123',
        'user': {
            'email': 'ict.dev@infracom-tech.com',
            'name': 'ICT Admin'
        },
        'auth': {
            'collaboration': {
                '*': {
                    'role': 'writer'
                }
            }
        }
    }
    return jwt.encode(payload, CKEDITOR_COLLAB_ACCESS_KEY)

def hash_password(password: str):
    return bcrypt.hashpw(str.encode(password), bcrypt.gensalt(12))

def check_password(password: str, hashed_pass:str):
    return bcrypt.checkpw(str.encode(password), str.encode(hashed_pass))