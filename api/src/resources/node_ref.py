from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigModel, NodeModel


class NodeReferences(Resource):

    """"
    Node references resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, node_id: str):
        references = [{
            "name": "config",
            "items": [c.get(get_repo=True) for c in ConfigModel.query.join(
                NodeModel,
                NodeModel.id == ConfigModel.node_id,
                isouter=True
            ).filter(ConfigModel.node_id == node_id)]
        }]
        return references
