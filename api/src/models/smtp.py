import json
from os import path, remove
from respect_validation import Validator as v, FormValidator

from api.config import GlobalConfig
from configtracker.mail_service import MailService
from api.src.encryptor import Encryptor


class SMTPModel:

    settings: dict = {
        "server": [],
        "auth": True,
        "port": 465,
        "secure": "ssl",
        "username": "",
        "password": "",
        "from": "",
        "base_url": ""
    }

    settings_file = f"{GlobalConfig.SETTINGS_DIR}/smtp.json"

    @staticmethod
    def fv() -> 'FormValidator':
        return FormValidator()

    def __init__(self):
        self.settings = {**SMTPModel.settings}
        if not path.isfile(self.settings_file):
            with open(self.settings_file, 'w') as settings:
                settings.write(json.dumps(self.settings, indent=4))
        else:
            try:
                with open(self.settings_file, 'r') as settings:
                    self.settings = json.load(settings)
            except:
                remove(self.settings_file)
                self.settings = {**SMTPModel.settings}

    def validate(self, settings):
        rules = {
            'server': v.stringType().notEmpty(),
            'base_url': v.stringType().notEmpty(),
            'auth': v.boolType(),
            'port': v.IntType().notEmpty().between(1, 64000),
            'secure': v.stringType().notEmpty().include(['none', 'ssl', 'tls']),
            'from': v.stringType().notEmpty().email(),
            'username': v.Optional(v.stringType().notEmpty().email()),
            'password': v.Optional(v.stringType().notEmpty().email())
        }

        if settings.get('auth', False):
            rules['username'] = v.stringType().notEmpty()

        if settings.get('auth', False) and (not self.settings["password"] or settings["password"]):
            rules['password'] = v.stringType().notEmpty()

        return self.fv().validate(settings, rules)

    def validate_test(self, data):
        rules = {
            'email': v.stringType().notEmpty().email()
        }
        return self.fv().validate(data, rules)

    def get(self):
        return {**self.settings, 'password': ""}

    def save(self, settings):
        if settings["password"]:
            settings["password"] = Encryptor.run(settings["password"])
        else:
            settings["password"] = self.settings["password"]
        self.settings = {**self.settings, **settings}
        with open(self.settings_file, 'w') as settings:
            settings.write(json.dumps(self.settings, indent=4))

    @staticmethod
    def test(email: str):
        try:
            ms = MailService()
            ms.set_template('hello.html').set_parameter("base_body_class", " card-email-body-hello")\
                .set_subject('ConfigTracker - Hello message')
            ms.send(email)
        except Exception as e:
            return True, str(e)
        return False, ''
