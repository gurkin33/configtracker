from respect_validation.Rules.AbstractRule import AbstractRule


class CredentialsInvalid(AbstractRule):

    def __init__(self, message: str):
        super().__init__()
        self.set_param('message', message)

    def validate(self, input_val) -> bool:
        return False
