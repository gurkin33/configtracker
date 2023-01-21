from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import ScriptModel


class ScriptExists(AbstractRule):

    def validate(self, input_val) -> bool:
        _id = str(input_val)
        return bool(ScriptModel.query.filter(ScriptModel.id == _id).first())
