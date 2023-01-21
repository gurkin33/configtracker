import pexpect

from configtracker import log
from configtracker import Decrypter
# from api.src.engine import GitHandler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from configtracker.models.config import ConfigModel


class ScriptExpectEngine:

    @staticmethod
    def run(config: 'ConfigModel', pex):
        # full_log = ''
        output = ''
        log.debug("Start script")
        for i, expectation in enumerate(config.script.expect.expectations):
            timeout = config.script.expect.timeout
            pex.timeout = config.script.expect.timeout
            if expectation.timeout:
                log.debug(f"Expectation has own timeout: {expectation.timeout}")
                pex.timeout = expectation.timeout
                timeout = expectation.timeout

            if i + 1 == len(config.script.expect.expectations) and len(expectation.prompt) == 0:
                log.debug(f"It is the last command and it expects nothing")
                if expectation.secret:
                    log.info(f"Script send cmd: ******")
                else:
                    log.info(f"Script send cmd: {expectation.cmd}")
                pex.sendline(Decrypter.run(expectation.cmd))
                log.debug(f"Connection close for {config.name}")
                pex.close()
                log.debug(f"Script exit")
                if output == '':
                    raise Exception('Final output is empty!')
                return output

            if len(expectation.prompt) == 0:
                log.debug(f"Expectation prompt empty. Break expectation loop")
                log.info(f"Script send cmd as expected: {expectation.cmd}")
                pex.sendline(Decrypter.run(expectation.cmd))
                log.debug(f"Connection close for {config.name}")
                pex.close()
                log.debug(f"Script exit")
                if output == '':
                    raise Exception('Final output is empty!')
                return output

            # log.debug(f"Script expect prompt before send: {expectation.prompt}")
            # pex.expect(expectation.prompt, timeout=timeout)
            log.debug(f"Ssh before send: {pex.before}")
            if expectation.secret:
                log.info(f"Script send cmd: ******")
            else:
                log.info(f"Script send cmd: {expectation.cmd}")
            pex.sendline(Decrypter.run(expectation.cmd))

            log.debug(f"Script expect prompt before action: {expectation.prompt}")
            pex.expect(expectation.prompt, timeout=timeout)
            log.debug(f"Command output: {pex.before}")
            if expectation.save:
                log.debug(f"Script save output")
                _output = str(pex.before).split("\n")
                if expectation.skip_top:
                    log.debug(f"Script skip {expectation.skip_top} top lines")
                    _output = _output[expectation.skip_top + 1:]
                if expectation.skip_bottom:
                    log.debug(f"Script skip {expectation.skip_bottom} bottom lines")
                    _output = _output[:(expectation.skip_bottom * -1)]
                output = "\n".join(_output)
            else:
                log.debug("Script there is no action for this expect")

        log.debug(f"Connection close for {config.name}")
        pex.close()
        log.debug(f"Script exit")
        if output == '':
            raise Exception('Final output is empty!')
        return output
