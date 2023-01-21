from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import ConfigModel


class ConfigExists(AbstractRule):

    def __init__(self, repo_id: str = None):
        super().__init__()
        self._repo_id = repo_id

    def validate(self, input_val) -> bool:
        if not self._repo_id:
            return bool(ConfigModel.query.filter(ConfigModel.id == input_val).first())

        return bool(ConfigModel.query.filter(ConfigModel.id == input_val).filter(
            ConfigModel.repo_id == self._repo_id).first())
