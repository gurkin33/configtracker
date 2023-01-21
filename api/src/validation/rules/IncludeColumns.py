from typing import List

from respect_validation.Rules.AbstractRule import AbstractRule


class IncludeColumns(AbstractRule):

    def __init__(self, columns: List):
        super().__init__()
        self._columns = columns
        self.set_param('columns', columns)

    def validate(self, input_val) -> bool:

        return input_val in self._columns
