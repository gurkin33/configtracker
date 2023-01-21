from respect_validation.Exceptions import ValidationException


class IncludeColumnsException(ValidationException):

    _default_templates = {
        'default': {
            'standard': 'Column {name} out of column list {columns}'
        },
        'negative': {
            'standard': 'Column {name} is in column list {columns}'
        }
    }
