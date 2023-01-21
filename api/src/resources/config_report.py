from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigReportModel, ConfigModel


class ConfigReport(Resource):

    """"
    Config report resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, config_id: str = ''):

        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        reports = ConfigReportModel.query.filter(ConfigReportModel.config_id == config.id).all()
        return [r.get() for r in reports], 200
