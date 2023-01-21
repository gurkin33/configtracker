from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import CredentialsModel


class CredentialsExists(AbstractRule):

    def validate(self, input_val) -> bool:
        _id = str(input_val)
        return bool(CredentialsModel.query.filter(CredentialsModel.id == _id).first())
