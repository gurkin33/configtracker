from respect_validation.Exceptions import ValidationException


class Script2CredentialsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': '{message}'
        },
        'negative': {
            'standard': '{message}'
        }
    }