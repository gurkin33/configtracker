from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from api.src import access_checker
from api.src.models.smtp import SMTPModel


class Smtp(Resource):

    """"
    Smtp resource
    """
    @classmethod
    @access_checker([], True)
    def get(cls):
        smtp = SMTPModel()
        return smtp.get()

    @classmethod
    @access_checker([])
    def post(cls):
        settings = request.get_json()
        smtp = SMTPModel()
        v = smtp.validate(settings)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        smtp.save(settings)
        return True


class SmtpTest(Resource):

    """"
    Smtp test resource
    """

    @classmethod
    @access_checker([])
    def post(cls):
        data = request.get_json()
        smtp = SMTPModel()
        v = smtp.validate_test(data)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        error, message = smtp.test(data['email'])
        if error:
            return {'errors': [message]}, 400
        return True
