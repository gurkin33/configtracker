from functools import wraps
from typing import List
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def access_checker(permissions: List[str] = [], allow_demo: bool = False):
    def admin_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user = claims.get('user')
            if not user:
                return {"error": ['Access Restricted!']}, 401
            if 'all' in permissions and user.get('permissions', []) != ['demo']:
                return fn(*args, **kwargs)
            # if claims.get('change_pw', False):
            #     return {"message": 'Please change your password', "change_pw": True}, 403
            if 'admin' in user.get('permissions', []) or (allow_demo and 'demo' in user.get('permissions', [])):
                return fn(*args, **kwargs)
            if set(permissions).intersection(set(user.get('permissions', []))):
                return fn(*args, **kwargs)
            else:
                return {"error": ['Access Restricted!']}, 403
        return wrapper
    return admin_required


def access_checker_(permissions: List[str] = [], allow_demo: bool = False):
    verify_jwt_in_request()
    claims = get_jwt()
    user = claims.get('user')
    if not user:
        return False
    if 'all' in permissions:
        return True
    if 'admin' in user.get('permissions', []) or (allow_demo and 'demo' in user.get('permissions', [])):
        return True
    if set(permissions).intersection(set(user.get('permissions', []))):
        return True
    else:
        return False
