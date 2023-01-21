from flask_restful import Resource

from api.src import access_checker
from api.src.models import SessionModel


class Session(Resource):
    """"
    Session resource
    """

    @classmethod
    @access_checker([])
    def delete(cls, session_id: int = ''):
        if not session_id:
            return {"error": ["Session ID must be present!"]}, 400
        session = SessionModel.find_by_id(_id=session_id)
        if not session:
            return {"error": ["Session not found"]}, 404

        session.delete()

        return {"result": True}, 200
