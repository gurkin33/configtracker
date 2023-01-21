from flask_restful import Resource

from api.src import access_checker
from api import __version__


class ProjectVersion(Resource):

    """"
    Get version resource
    """

    @classmethod
    @access_checker(['all'], True)
    def get(cls):
        return __version__
