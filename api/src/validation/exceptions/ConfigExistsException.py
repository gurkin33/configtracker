from respect_validation.Exceptions import ValidationException


class ConfigExistsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': 'Config not exists'
        },
        'negative': {
            'standard': 'Config already exists'
        }
    }
