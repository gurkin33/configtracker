from respect_validation.Exceptions import ValidationException


class CheckRepoGroupParentException(ValidationException):

    _default_templates = {
        'default': {
            'standard': 'Group cannot be parent for yourself'
        },
        'negative': {
            'standard': 'Group must be parent for yourself?'
        }
    }
