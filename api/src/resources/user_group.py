from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.models.user_group import UserGroupModel, UserGroupPermissions


class UserGroup(Resource):

    """"
    User group resource is CRUD class
    """

    @classmethod
    @access_checker([], True)
    def get(cls, group_id: str = ''):
        if not group_id:
            return {"error": ["User group ID must be present!"]}, 400
        group = UserGroupModel.find_by_id(_id=group_id)
        if not group:
            return {"error": ["User group not found"]}, 404
        return group.get(), 200

    @classmethod
    @access_checker([])
    def post(cls):
        group_json = request.get_json()
        v = UserGroupModel.validate(group=group_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        _permissions = group_json['permissions']
        del group_json['permissions']
        new_group = UserGroupModel(**group_json)
        new_group.save()

        permissions = []
        for permission in _permissions:
            permissions.append(UserGroupPermissions(permission=permission, user_group_id=new_group.id))

        # UserGroupPermissions.bulk_insert(permissions)
        new_group.permissions = permissions
        new_group.save()

        return new_group.get(), 200

    @classmethod
    @access_checker([])
    def put(cls, group_id: str = ''):
        if not group_id:
            return {"error": ["User group ID must be present!"]}, 400
        group = UserGroupModel.find_by_id(_id=group_id)
        if not group:
            return {"error": ["User group not found"]}, 404

        group_json = request.get_json()
        v = UserGroupModel.validate(group=group_json, _id=group_id)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        _permissions = group_json['permissions']
        permissions = []
        for permission in _permissions:
            permissions.append(UserGroupPermissions(permission=permission, user_group_id=group.id))
        group_json['permissions'] = permissions

        group.update(data=group_json)
        group.save()

        return group.get(), 200

    @classmethod
    @access_checker([])
    def delete(cls, group_id: int = 0):
        if not group_id:
            return {"error": ["User group ID must be present!"]}, 400
        group = UserGroupModel.find_by_id(_id=group_id)
        if not group:
            return {"error": ["User group not found"]}, 404

        if UserGroupModel.get_ref_count(group_id):
            return {"error": ["User group has references!"]}, 400

        group.delete()

        return {"result": True}, 200
