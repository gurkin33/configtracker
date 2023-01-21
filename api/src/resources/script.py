import re

from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.encryptor import Encryptor
from api.src.models import ScriptModel, ScriptExpectModel, ScriptFileTransferModel, ScriptWgetModel, ExpectationModel


class Script(Resource):

    """"
    Script resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, script_id: str = ''):
        if not script_id:
            return {"error": ["Script ID must be present!"]}, 400
        script = ScriptModel.find_by_id(_id=script_id)
        if not script:
            return {"error": ["Script not found"]}, 404
        return script.get(), 200

    @classmethod
    @access_checker(['manager'])
    def post(cls):
        script_json = request.get_json()
        v = ScriptModel.validate(script=script_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        if script_json.get('wget', None) is not None:
            v = ScriptWgetModel.validate(script_wget=script_json['wget'])
            if v.failed():
                return {'validation_wget': v.get_messages()}, 400
            script_json['wget'] = ScriptWgetModel(**script_json['wget'])

        if script_json.get('expect', None) is not None:
            _expectations = []
            v = ScriptExpectModel.validate(script_expect=script_json['expect'])
            if v.failed():
                return {'validation_expect': v.get_messages()}, 400
            for ex in script_json['expect']['expectations']:
                if 'id' in ex.keys():
                    del ex['id']
                if 'script_id' in ex.keys():
                    del ex['script_id']
                if ex['secret'] and not re.search(r'fernet\((.*?)\)', ex['cmd']):
                    ex['cmd'] = Encryptor.run(ex['cmd'])
                _expectations.append(ExpectationModel(**ex))
            script_json['expect']['expectations'] = _expectations
            script_json['expect'] = ScriptExpectModel(**script_json['expect'])

        if script_json.get('file_transfer', None) is not None:
            v = ScriptFileTransferModel.validate(script_file_transfer=script_json['file_transfer'])
            if v.failed():
                return {'validation_file_transfer': v.get_messages()}, 400
            script_json['file_transfer'] = ScriptFileTransferModel(**script_json['file_transfer'])

        new_script = ScriptModel(**script_json)
        new_script.save()

        return new_script.get(), 200

    @classmethod
    @access_checker(['manager'])
    def put(cls, script_id: str = ''):
        if not script_id:
            return {"error": ["Script ID must be present!"]}, 400
        script = ScriptModel.find_by_id(_id=script_id)
        if not script:
            return {"error": ["Script not found"]}, 404

        script_json = request.get_json()

        v = ScriptModel.validate(script=script_json, _id=script.id)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        if script_json.get('wget', None) is not None:
            v = ScriptWgetModel.validate(script_wget=script_json['wget'])
            if v.failed():
                return {'validation_wget': v.get_messages()}, 400
            if script.wget is not None:
                script.wget.delete()
            script_json['wget'] = ScriptWgetModel(**script_json['wget'])
        elif 'wget' in script_json.keys():
            del script_json['wget']

        if script_json.get('file_transfer', None) is not None:
            v = ScriptFileTransferModel.validate(script_file_transfer=script_json['file_transfer'])
            if v.failed():
                return {'validation_file_transfer': v.get_messages()}, 400
            if script.file_transfer is not None:
                script.file_transfer.delete()
            script_json['file_transfer'] = ScriptFileTransferModel(**script_json['file_transfer'])
        elif 'file_transfer' in script_json.keys():
            del script_json['file_transfer']

        if script_json.get('expect', None) is not None:
            v = ScriptExpectModel.validate(script_expect=script_json['expect'])
            if v.failed():
                return {'validation_expect': v.get_messages()}, 400
            if script.expect is not None:
                script.expect.delete()
            _expectations = []
            for ex in script_json['expect']['expectations']:
                if 'id' in ex.keys():
                    del ex['id']
                if 'script_id' in ex.keys():
                    del ex['script_id']
                if ex['secret']:
                    ex['cmd'] = Encryptor.run(ex['cmd'])
                _expectations.append(ExpectationModel(**ex))
            script_json['expect']['expectations'] = _expectations
            script_json['expect'] = ScriptExpectModel(**script_json['expect'])
        elif 'expect' in script_json.keys():
            del script_json['expect']

        script.update(data=script_json)
        script.save()

        return script.get(), 200

    @classmethod
    @access_checker(['manager'])
    def delete(cls, script_id: int = 0):
        if not script_id:
            return {"error": ["Script ID must be present!"]}, 400
        script = ScriptModel.find_by_id(_id=script_id)
        if not script:
            return {"error": ["Script not found"]}, 404

        if ScriptModel.get_ref_count(script_id):
            return {"error": ["Script has references!"]}, 400

        script.delete()

        return {"result": True}, 200
