from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.encryptor import Encryptor
from api.src.models import CredentialsModel


class Credentials(Resource):

    """"
    Credentials resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, credentials_id: str = ''):
        if not credentials_id:
            return {"error": ["Credentials ID must be present!"]}, 400
        creds = CredentialsModel.find_by_id(_id=credentials_id)
        if not creds:
            return {"error": ["Credentials not found"]}, 404
        data = creds.get()
        data["password"] = ""
        data["ssh_key"] = ""
        return data, 200

    @classmethod
    @access_checker(['manager'])
    def post(cls):
        credentials_json = request.get_json()
        v = CredentialsModel.validate(credentials=credentials_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        if credentials_json.get('password', None) and credentials_json['password']:
            credentials_json['password'] = Encryptor.run(credentials_json['password'])
        if credentials_json.get('ssh_key', None) and credentials_json['ssh_key']:
            credentials_json['ssh_key'] = Encryptor.run(credentials_json['ssh_key'])
        new_credentials = CredentialsModel(**credentials_json)
        new_credentials.save()

        return new_credentials.get(), 200

    @classmethod
    @access_checker(['manager'])
    def put(cls, credentials_id: str = ''):
        if not credentials_id:
            return {"error": ["Credentials ID must be present!"]}, 400
        credentials = CredentialsModel.find_by_id(_id=credentials_id)
        if not credentials:
            return {"error": ["Credentials not found"]}, 404

        credentials_json = request.get_json()

        if 'password' in credentials_json.keys() and not credentials_json['password']:
            del credentials_json['password']

        if 'ssh_key' in credentials_json.keys() and not credentials_json['ssh_key']:
            del credentials_json['ssh_key']

        v = CredentialsModel.validate(credentials=credentials_json, _id=credentials_id)

        if v.failed():
            return {'validation': v.get_messages()}, 400

        credentials.update(data=credentials_json)
        credentials.save()

        return credentials.get(), 200

    @classmethod
    @access_checker(['manager'])
    def delete(cls, credentials_id: str = ''):
        if not credentials_id:
            return {"error": ["Credentials ID must be present!"]}, 400
        credentials = CredentialsModel.find_by_id(_id=credentials_id)
        if not credentials:
            return {"error": ["Credentials not found"]}, 404

        if CredentialsModel.get_ref_count(credentials_id):
            return {"error": ["Credentials has references!"]}, 400

        credentials.delete()

        return {"result": True}, 200
