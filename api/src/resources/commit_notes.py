from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigModel, CommitNotesModel, ConfigBinModel


class CommitNotes(Resource):

    """"
    Config commit notes resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, config_id: str, commit: str):
        bin_ = request.path.startswith('/api/bin/')
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        if bin_:
            config = ConfigBinModel.find_by_id(_id=config_id)
        else:
            config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        if not config.commit_exists(commit):
            return {"error": ["Commit not found"]}, 404

        notes = CommitNotesModel.find_(config_id, commit, bin_=bin_)

        return notes.get() if notes else None

    @classmethod
    @access_checker(['manager'])
    def post(cls, config_id: str, commit: str):
        bin_ = request.path.startswith('/api/bin/')
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        if bin_:
            config = ConfigBinModel.find_by_id(_id=config_id)
        else:
            config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        if not config.commit_exists(commit):
            return {"error": ["Commit not found"]}, 404

        data = request.get_json()
        v = CommitNotesModel.validate(data=data)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        notes = CommitNotesModel.save_data(config_id=config_id, commit=commit, data=data, bin_=bin_)

        return notes.get()

