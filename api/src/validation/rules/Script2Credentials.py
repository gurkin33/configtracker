from respect_validation.Rules.AbstractRule import AbstractRule
from api.src.models.script import ScriptModel
from api.src.models.credentials import CredentialsModel


class Script2Credentials(AbstractRule):

    def __init__(self, creds_id: str):
        super().__init__()
        self._creds_id = creds_id

    def validate(self, input_val) -> bool:
        message = None
        if not input_val:
            return True
        script = ScriptModel.find_by_id(input_val)
        if not script:
            return True

        creds = CredentialsModel.find_by_id(self._creds_id) if self._creds_id else None

        # Access:
        # wget - creds: any
        # expect_ssh - creds: username/password, ssh_key
        # expect_telnet - creds: username/password, password_only
        # ft_sftp - creds: username/password, ssh_key
        # ft_ftp - creds: username/password
        # creds types: ['user-creds', 'password', 'ssh-key']

        if script.file_transfer_id:
            if script.file_transfer.protocol == 'sftp':
                if not creds or creds.type not in ['user-creds', 'ssh-key']:
                    message = "Credentials required and must be username/password or SSH key"

        if script.file_transfer_id:
            if script.file_transfer.protocol == 'ftp':
                if not creds or creds.type not in ['user-creds']:
                    message = "Credentials required and must be username/password"

        if script.expect_id:
            if script.expect.protocol == 'ssh':
                if not creds or creds.type not in ['user-creds', 'ssh-key']:
                    message = "Credentials required and must be username/password or SSH key"

        if script.expect_id:
            if script.expect.protocol == 'telnet':
                if not creds or creds.type not in ['user-creds', 'password']:
                    message = "Credentials required and must be username/password or password only"

        self.set_param('message', message)

        return message is None
