from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigModel, ScriptModel


class ScriptReferences(Resource):

    """"
    Script references resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, script_id: str):
        references = [{
            "name": "config",
            "items": [c.get(get_repo=True) for c in ConfigModel.query.join(
                ScriptModel,
                ScriptModel.id == ConfigModel.script_id,
                isouter=True
            ).filter(ConfigModel.script_id == script_id)]
        }]
        return references
