from respect_validation.Exceptions import ValidationException


class NotificationsRepoGroupException(ValidationException):

    _default_templates = {
        'default': {
            'standard': '{name} already exists'
        },
        'negative': {
            'standard': '{name} not exists yet'
        }
    }
