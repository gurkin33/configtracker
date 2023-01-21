from respect_validation.Exceptions import ValidationException


class AddressNotExistsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': '{name} already exists'
        },
        'negative': {
            'standard': '{name} not exists'
        }
    }
