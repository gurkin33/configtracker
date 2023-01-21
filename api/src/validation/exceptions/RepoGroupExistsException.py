from respect_validation.Exceptions import ValidationException


class RepoGroupExistsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': 'Repository group not exists'
        },
        'negative': {
            'standard': 'Repository group already exists'
        }
    }
