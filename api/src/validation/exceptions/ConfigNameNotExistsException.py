from respect_validation.Exceptions import ValidationException


class ConfigNameNotExistsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': '{name} exists'
        },
        'negative': {
            'standard': '{name} not exists'
        }
    }
