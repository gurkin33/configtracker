import uuid
import pexpect

from api.config import GlobalConfig
from configtracker import log
from configtracker.engine import ScriptExpectEngine, ConfigFile
from configtracker import Decrypter
from configtracker.engine.connectors.connector_manager import ConnectorManager
from configtracker.engine.error_reporter import ErrorReporter
from configtracker.engine.git_handler import GitHandler
from configtracker.models.config import ConfigModel


class SshConnector:

    @staticmethod
    def run(config: ConfigModel, test: bool = False):
        log.info(f"Ssh connector activated")
        connection_timeout = (config.script.expect.timeout - 1) if config.script.expect.timeout > 1 \
            else config.script.expect.timeout
        ssh_key = ''
        if config.credentials is None:
            log.error("Missed credentials! Credentials required!")
            if not test:
                ErrorReporter.add(config.id, "Credentials required!")
                return False
            else:
                return {"error": True, "output": ""}
        if config.credentials.type == 'ssh-key':
            random_uuid = str(uuid.uuid4())
            log.info(f"Credentials type SSH Key")
            ConnectorManager.ssh_key_prepare(Decrypter.run(config.credentials.ssh_key), random_uuid)
            ssh_key = f"-i {GlobalConfig.TEMP_DIR}/{random_uuid}.ssh.key"

        connection_cmd = f'ssh {ssh_key} -tt -oStrictHostKeyChecking=no -p {config.script.expect.port} -o ' \
                  f'ConnectTimeout={connection_timeout} ' \
                  f'{config.credentials.username}@{config.node.address}'
        log.debug(f"Command: {connection_cmd}")

        pex_child = pexpect.spawn(connection_cmd, encoding='utf8')
        pex_child.timeout = config.script.expect.timeout

        if not ssh_key:

            try:
                if config.credentials.password is not None:
                    pex_child.expect(config.script.expect.password_prompt)
                    log.debug(f"Ssh send password")
                    pex_child.sendline(Decrypter.run(config.credentials.password))
                else:
                    log.warning(f"Ssh password is None")
            except Exception as e:
                if type(e) is pexpect.exceptions.TIMEOUT:
                    ErrorReporter.add(config.id,
                                      f"Ssh authentication timeout error! Last output: {str(pex_child.before).strip()}")
                    ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
                else:
                    ErrorReporter.add(config.id, f"Ssh authentication unexpected exception: {e}")
                    ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
                if not test:
                    ErrorReporter.add(config.id, "Config exit with error")
                    return False
                return {"error": True, "output": ""}
        else:
            log.debug("SSH Key was used skip password check")

        try:
            log.debug(f"Ssh before default prompt: {pex_child.before}")
            log.debug(f"Ssh expect default prompt: {config.script.expect.default_prompt}")
            pex_child.expect(config.script.expect.default_prompt)
        except Exception as e:
            if type(e) is pexpect.exceptions.TIMEOUT:
                ErrorReporter.add(config.id,
                                  f"Ssh default prompt timeout error! Last output: {str(pex_child.before).strip()}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            else:
                ErrorReporter.add(config.id, f"Ssh default prompt unexpected exception: {e}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            output = ScriptExpectEngine.run(config, pex_child)
        except Exception as e:
            if type(e) is pexpect.exceptions.TIMEOUT:
                ErrorReporter.add(config.id, f"Ssh script timeout error! Last output: {str(pex_child.before).strip()}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            else:
                ErrorReporter.add(config.id, f"Ssh script unexpected exception: {e}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}
        if test:
            return {"error": False, "output": output}

        log.info("Add output to git")
        file = ConfigFile.data_from_str(output)
        config.status_ = True
        GitHandler.add(config, file)

        return True
