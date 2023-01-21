from flask import request
from flask_jwt_extended import get_jwt
from flask_restful import Resource
from sqlalchemy import or_

from api.src import access_checker, access_checker_
from api.src.datatables import DataTables, DatatablesValidator

from api.src.models import ConfigModel, UserModel, NotificationsConfigModel, UserGroupModel, UserGroupMembers


class DataTablesSubscriptions(DataTables):

    user_id: str = ""

    def after_query_init(self, query):
        return query.join(
                NotificationsConfigModel,
                NotificationsConfigModel.config_id == ConfigModel.id,
                isouter=True
            ).join(
                UserGroupModel,
                UserGroupModel.id == NotificationsConfigModel.group_id,
                isouter=True
            ).join(
                UserGroupMembers,
                UserGroupMembers.c.user_group_id == UserGroupModel.id,
                isouter=True
            ).filter(or_(
                NotificationsConfigModel.user_id == self.user_id,
                UserGroupMembers.c.user_id == self.user_id
            )).group_by(ConfigModel.id)


class UserSubscriptionsTable(Resource):

    """"
    User subscriptions table resource
    """

    @classmethod
    @access_checker(['all'], True)
    def post(cls, user_id: str):
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

        params = request.get_json()

        dtv = DatatablesValidator.validate(params, ConfigModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTablesSubscriptions(params, ConfigModel)
        dt.user_id = user_id

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [row.get(get_repo=True) for row in result.all()]
        }
