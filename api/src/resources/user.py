from flask import request
from flask_jwt_extended import get_jwt
from flask_restful import Resource

from api.src import access_checker, access_checker_
from api.src.models.user import UserModel
from api.src.models.user_group import UserGroupModel


class User(Resource):
    """"
    User resource is CRUD class
    """

    @classmethod
    @access_checker(['all'], True)
    def get(cls, user_id: str = ''):
        if not user_id:
            return {"error": ["User ID must be present!"]}, 400
        user = UserModel.find_by_id(_id=user_id)
        if not user:
            return {"error": ["User not found"]}, 404
        if not access_checker_([], True):
            claims = get_jwt()
            _user = claims.get('user')
            if not _user:
                return {"error": ['Access Restricted!']}, 401
            if _user.get('id') != user_id:
                return {"error": ['Access Restricted!']}, 403
        return user.get(), 200

    @classmethod
    @access_checker([])
    def post(cls):
        user_json = request.get_json()
        v = UserModel.validate(user=user_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        user_json['groups'] = UserGroupModel.find_all_id(list([x['id'] for x in user_json["groups"]]))
        # print(user_json['groups'])

        user_json['password'] = UserModel.hash_password(user_json['password'])

        new_user = UserModel(**user_json)
        new_user.save()

        return new_user.get(), 200

    @classmethod
    @access_checker(['all'], False)
    def put(cls, user_id: str = ''):
        if not user_id:
            return {"error": ["User ID must be present!"]}, 400
        user = UserModel.find_by_id(_id=user_id)
        if not user:
            return {"error": ["User not found"]}, 404

        user_json = request.get_json()
        if not access_checker_([], True):
            claims = get_jwt()
            _user = claims.get('user')
            if not _user:
                return {"error": ['Access Restricted!']}, 401
            if _user.get('id') != user_id:
                return {"error": ['Access Restricted!']}, 403
            # edit profile mode
            if 'username' in user_json.keys():
                del user_json['username']
            if 'groups' in user_json.keys():
                del user_json['groups']

        if user_json.get('username', None) is None and 'groups' in user_json.keys():
            del user_json['groups']

        if 'password' in user_json.keys() and not user_json['password']:
            del user_json['password']
        v = UserModel.validate(user=user_json, _id=user_id, mode='edit')
        if v.failed():
            return {'validation': v.get_messages()}, 400
        if 'groups' in user_json.keys():
            user_json['groups'] = UserGroupModel.find_all_id(list([x['id'] for x in user_json["groups"]]))
        if 'password' in user_json.keys():
            user_json['password'] = UserModel.hash_password(user_json['password'])

        user.update(data=user_json)
        user.save()

        return user.get(), 200

    @classmethod
    @access_checker([])
    def delete(cls, user_id: int = ''):
        if not user_id:
            return {"error": ["User ID must be present!"]}, 400
        user = UserModel.find_by_id(_id=user_id)
        if not user:
            return {"error": ["User not found"]}, 404

        user.delete()

        return {"result": True}, 200


class UserInfo(Resource):
    """"
    Get current user info
    """

    @classmethod
    @access_checker(['all'], True)
    def get(cls):
        claims = get_jwt()
        _user = claims.get('user', None)
        if not _user:
            return {"error": ["User not found"]}, 401

        if _user.get('id', None):
            user = UserModel.find_by_id(_id=_user.get('id'))
            if user:
                return user.get(permissions=True)
        return {"error": ["User not found"]}, 401
