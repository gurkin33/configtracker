from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import NodeModel


class AddressNotExists(AbstractRule):

    _node_id: str = ''

    def __init__(self, node_id: str = ''):
        super().__init__()
        self._node_id = node_id

    def validate(self, input_val) -> bool:
        _address = str(input_val)
        return not bool(NodeModel.query.filter(NodeModel.address == _address, NodeModel.id != self._node_id).first())
