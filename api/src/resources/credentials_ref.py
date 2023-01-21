from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigModel, CredentialsModel


class CredentialsReferences(Resource):

    """"
    Credentials references resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, credentials_id: str):
        references = [{
            "name": "config",
            "items": [c.get(get_repo=True) for c in ConfigModel.query.join(
                CredentialsModel,
                CredentialsModel.id == ConfigModel.id,
                isouter=True
            ).filter(ConfigModel.credentials_id == credentials_id)]
        }]
        return references
