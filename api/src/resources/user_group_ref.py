from flask_restful import Resource

from api.src import access_checker
from api.src.models import UserModel, UserGroupMembers


class UserGroupReferences(Resource):

    """"
    User group references resource
    """

    @classmethod
    @access_checker([], True)
    def get(cls, group_id: str):
        references = [{
            "name": "config",
            "items": [c.get() for c in UserModel.query.join(
                UserGroupMembers,
                UserGroupMembers.c.user_id == UserModel.id,
                isouter=True
            ).filter(UserGroupMembers.c.user_group_id == group_id)]
        }]
        return references
