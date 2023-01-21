from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.datatables import DataTables, DatatablesValidator

from api.src.models import SessionModel


class SessionTable(Resource):

    """"
    User session table resource
    """

    @classmethod
    @access_checker([], True)
    def post(cls):
        params = request.get_json()
        dtv = DatatablesValidator.validate(params, SessionModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTables(params, SessionModel)

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [row.get() for row in result.all()]
        }
