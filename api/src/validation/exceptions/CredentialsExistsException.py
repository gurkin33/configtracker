from respect_validation.Exceptions import ValidationException


class CredentialsExistsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': '{name} not exists'
        },
        'negative': {
            'standard': '{name} already exists'
        }
    }
