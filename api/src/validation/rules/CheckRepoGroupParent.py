from respect_validation.Rules.AbstractRule import AbstractRule


class CheckRepoGroupParent(AbstractRule):

    _repo_group_id: str = ''

    def __init__(self, repo_group_id: str = ''):
        super().__init__()
        self._repo_group_id = repo_group_id

    def validate(self, input_val) -> bool:
        return self._repo_group_id != str(input_val)
