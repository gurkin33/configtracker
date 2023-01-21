from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import RepositoryModel


class RepoExists(AbstractRule):

    def validate(self, input_val) -> bool:
        _id = input_val
        return bool(RepositoryModel.query.filter(RepositoryModel.id == _id).first())
