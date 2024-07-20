import jwt
from time import time
from .environment import CKEDITOR_COLLAB_ACCESS_KEY, CKEDITOR_COLLAB_ENV_ID

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

