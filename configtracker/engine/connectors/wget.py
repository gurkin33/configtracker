import magic
import requests
from requests.exceptions import ConnectTimeout

from configtracker import log
from configtracker.engine import Decoder, ConfigFile
from configtracker.engine.error_reporter import ErrorReporter
from configtracker.engine.git_handler import GitHandler
from configtracker.models import ConfigModel


class WgetConnector:

    @staticmethod
    def run(config: ConfigModel, test: bool = False):
        log.info(f"Wget connector activated")
        try:
            url = config.script.wget.link.format(node_address=config.node.address)
            log.debug(f"Link: {url}")
        except Exception as e:
            ErrorReporter.add(config.id, f"Incorrect link format: {config.script.wget.link}, {e}! Exit")
            log.warning("Link format must be like so: \n - https://{node_address}/ if you want to use address as "
                        "variable\n - https://example.com/ if you want to use direct address")
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            return {"error": True, "output": ""}

        try:
            r = requests.get(url, allow_redirects=True, verify=False, timeout=config.script.wget.timeout)
        except ConnectTimeout as e:
            ErrorReporter.add(config.id, f"Connection timeout error: {e}! Exit")
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            return {"error": True, "output": ""}
        except Exception as e:
            ErrorReporter.add(config.id, f"Connection error: {e}! Exit")
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            return {"error": True, "output": ""}

        if r.status_code != 200:
            ErrorReporter.add(config.id, f"Request status code is {r.status_code}. Must be 200! Exit")
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            return {"error": True, "output": ""}

        if test:
            content = Decoder.run(r.content)
            if content is None:
                log.debug(f'Looks like content is binary file, cannot decode this data')
                if test:
                    mime = magic.from_buffer(r.content, mime=True)
                    return {"error": False, "output": None, "mime": mime}
            return {"error": False, "output": content}

        log.info("Add output to git")
        file = ConfigFile(r.content)
        config.status_ = True
        GitHandler.add(config, file)

        return True
