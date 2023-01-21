from ftplib import FTP, FTP_TLS
from io import BytesIO

import magic

from configtracker import log, Decrypter
from configtracker.engine import Decoder, ConfigFile
from configtracker.engine.error_reporter import ErrorReporter
from configtracker.engine.git_handler import GitHandler
from configtracker.models import ConfigModel


class FtpConnector:

    @staticmethod
    def run(config: ConfigModel, test: bool = False):
        log.info(f"FTP connector activated")
        try:
            if config.script.file_transfer.ftp_secure:
                ftp = FTP_TLS()
            else:
                ftp = FTP()
            ftp.connect(
                host=config.node.address,
                port=config.script.file_transfer.port,
                timeout=config.script.file_transfer.timeout)
            ftp.login(user=config.credentials.username, passwd=Decrypter.run(config.credentials.password))
            if config.script.file_transfer.ftp_secure:
                ftp.prot_p()
            log.debug(f"Successfully connected")
        except Exception as e:
            ErrorReporter.add(config.id, f'Connection error!')
            ErrorReporter.add(config.id, f'Error: {e}')
            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            if not ftp.nlst(config.script.file_transfer.path):
                raise Exception("File doesn't exist! Exit")
        except Exception as e:
            ErrorReporter.add(config.id, f'Read file error!')
            ErrorReporter.add(config.id, f'Error: {e}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            if ftp.size(config.script.file_transfer.path) is None:
                raise Exception("Path is directory! Exit")
        except Exception as e:
            ErrorReporter.add(config.id, f'Error. Is it directory?')
            ErrorReporter.add(config.id, f'Error: {e}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            r = BytesIO()
            ftp.retrbinary(f'RETR {config.script.file_transfer.path}', r.write)
        except Exception as e:
            ErrorReporter.add(config.id, f'Read file error!')
            ErrorReporter.add(config.id, f'Error: {e}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        content = Decoder.run(r.getvalue())
        if content is None:
            log.debug(f'Looks like content is binary file, cannot decode this data')
            if test:
                mime = magic.from_buffer(r.getvalue(), mime=True)
                return {"error": False, "output": None, "mime": mime}
        if test:
            return {"error": False, "output": content}

        log.info("Add output to git")
        file = ConfigFile(r.getvalue())
        config.status_ = True
        GitHandler.add(config, file)

        ftp.close()

        return True
