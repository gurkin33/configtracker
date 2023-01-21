from respect_validation.Rules.AbstractRule import AbstractRule
from flask_sqlalchemy import Model


class ExistsInDb(AbstractRule):

    # _model: Model
    # _column = ''

    def __init__(self, model: Model, column: str = 'id'):
        super().__init__()
        self._model = model
        self._column = column

    def validate(self, input_val) -> bool:
        filter_data = dict()
        filter_data[self._column] = str(input_val)
        return bool(self._model.query.filter_by(**filter_data).first())
