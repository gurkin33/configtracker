from flask_restful import Resource

from api.src import access_checker


class UserGroupPermissions(Resource):

    """"
    User group permissions list resource is CRUD class
    """

    @classmethod
    @access_checker([], True)
    def get(cls):
        permissions = [
            {"name": "Administrator", "permissions": [{"admin": "Allow all"}]},
            {"name": "Demo", "permissions": [{"demo": "Allow view only for all"}]},
            {"name": "Configuration Manager", "permissions": [{"manager": "Allow configuration management"}]},
        ]
        return permissions
