from respect_validation.Exceptions import ValidationException


class CredentialsInvalidException(ValidationException):

    _default_templates = {
        'default': {
            'standard': '{message}'
        },
        'negative': {
            'standard': '{message}'
        }
    }