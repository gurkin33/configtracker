import io
from os.path import isfile

from flask import send_file, request
from flask_restful import Resource

from api.config import GlobalConfig
from api.src import access_checker
from api.src.models import ConfigModel, ConfigBinModel


class ConfigDownload(Resource):

    """"
    Config download resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, config_id: str, commit: str = ''):
        bin_ = request.path.startswith('/api/bin/')
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        if bin_:
            config = ConfigBinModel.find_by_id(_id=config_id)
        else:
            config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        if commit:
            if not config.commit_exists(commit):
                return {"error": ["Commit not found"]}, 404

        if commit:
            data = config.get_data(commit=commit, binary_ignore=False)
            if not data:
                return {"error": ["Commit is empty"]}, 404
            mem = io.BytesIO()
            mem.write(data.encode('utf-8','surrogateescape'))
            # seeking was necessary. Python 3.5.2, Flask 0.12.2 # comment from stackoverflow:
            # https://stackoverflow.com/questions/35710361/python-flask-send-file-stringio-blank-files
            # and this:
            # https://stackoverflow.com/questions/50003821/get-a-binary-file-from-gitpython-by-revision-got-unicodestring-want-bytes
            mem.seek(0)

            return send_file(
                mem,
                as_attachment=True,
                download_name=f"{config.name}-{commit}"
            )

        if bin_ and not commit:
            return {"error": ["Please add commit to get data from bin"]}, 400

        path = f"{GlobalConfig.REPOS_ROOT_PATH}/{config.repo_id}/{config.id}"
        if not isfile(path):
            return {"error": ["Config file not found"]}, 404

        return send_file(path, as_attachment=True, download_name=f"{config.name}")
