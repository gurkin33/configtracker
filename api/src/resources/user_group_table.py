from flask import request
from flask_restful import Resource

from api.src.datatables import DatatablesValidator, DataTables
from api.src.models import UserGroupModel
from api.src import access_checker


class UserGroupTable(Resource):

    """"
    User group table resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls):
        params = request.get_json()

        dtv = DatatablesValidator.validate(params, UserGroupModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTables(params, UserGroupModel)

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [{**row[0].get(), 'references': row[1]} for row in result.all()]
        }
