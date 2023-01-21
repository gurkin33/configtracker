from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.datatables import DataTables, DatatablesValidator

from api.src.models.user import UserModel


class UserTable(Resource):

    """"
    User table resource
    manager can get list of users for example to set notifications
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls):
        params = request.get_json()

        dtv = DatatablesValidator.validate(params, UserModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTables(params, UserModel)

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [row.get() for row in result.all()]
        }
