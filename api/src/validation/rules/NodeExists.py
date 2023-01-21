from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import NodeModel


class NodeExists(AbstractRule):

    def validate(self, input_val) -> bool:
        _id = str(input_val)
        return bool(NodeModel.query.filter(NodeModel.id == _id).first())
