import pexpect
from configtracker import log
from configtracker.engine import ScriptExpectEngine, ConfigFile
from configtracker import Decrypter
from configtracker.engine.error_reporter import ErrorReporter
from configtracker.engine.git_handler import GitHandler
from configtracker.models.config import ConfigModel


class TelnetConnector:

    @staticmethod
    def run(config: ConfigModel, test: bool = False):
        log.info(f"Telnet connector activated")
        command = f'telnet "{config.node.address}" {config.script.expect.port}'
        log.debug(f"Command: {command}")
        pex_child = pexpect.spawn(command, encoding='utf8')
        pex_child.timeout = config.script.expect.timeout

        try:
            if config.credentials.username:
                pex_child.expect(config.script.expect.username_prompt)
                log.debug(f"Telnet send username {config.credentials.username}")
                pex_child.sendline(config.credentials.username)
            else:
                log.warning(f"Telnet username is empty. Skip this step")
        except Exception as e:
            if type(e) is pexpect.exceptions.TIMEOUT:
                ErrorReporter.add(config.id,
                                  f"Telnet username timeout error! Last output: {str(pex_child.before).strip()}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            else:
                ErrorReporter.add(config.id, f"Telnet username unexpected exception: {e}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            if config.credentials.password:
                pex_child.expect(config.script.expect.password_prompt)
                log.debug(f"Telnet send password")
                pex_child.sendline(Decrypter.run(config.credentials.password))
            else:
                log.warning(f"Telnet password is empty!")
        except Exception as e:
            if type(e) is pexpect.exceptions.TIMEOUT:
                ErrorReporter.add(config.id,
                                  f"Telnet password timeout error! Last output: {str(pex_child.before).strip()}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            else:
                ErrorReporter.add(config.id, f"Telnet password unexpected exception: {e}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            log.debug(f"Telnet expect default prompt: {config.script.expect.default_prompt}")
            pex_child.expect(config.script.expect.default_prompt)
        except Exception as e:
            if type(e) is pexpect.exceptions.TIMEOUT:
                ErrorReporter.add(config.id,
                                  f"Telnet default prompt timeout error! Last output: {str(pex_child.before).strip()}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            else:
                ErrorReporter.add(config.id, f"Telnet default prompt unexpected exception: {e}")
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
                ErrorReporter.add(config.id,
                                  f"Telnet script timeout error! Last output: {str(pex_child.before).strip()}")
                ErrorReporter.add(config.id, f'pexpect before: {pex_child.before}')
            else:
                ErrorReporter.add(config.id, f"Telnet script unexpected exception: {e}")
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
