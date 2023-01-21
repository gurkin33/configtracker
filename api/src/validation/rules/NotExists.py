from respect_validation.Rules.AbstractRule import AbstractRule
from flask_sqlalchemy import Model


class NotExists(AbstractRule):

    _model: Model
    _column = ''
    _id = ''

    def __init__(self, model: Model, column: str = 'name', obj_id: str = None):
        super().__init__()
        self._model = model
        self._column = column
        self._id = obj_id

    def validate(self, input_val) -> bool:
        filter_data = dict()
        filter_data[self._column] = str(input_val)
        return not self._model.query.filter_by(**filter_data).filter(self._model.id != self._id).first()
