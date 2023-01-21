import uuid

import magic
import paramiko

from api.config import GlobalConfig
from configtracker import log, Decrypter
from configtracker.engine import Decoder, ConfigFile
from configtracker.engine.connectors.connector_manager import ConnectorManager
from configtracker.engine.error_reporter import ErrorReporter
from configtracker.engine.git_handler import GitHandler
from configtracker.models import ConfigModel
import stat


class SftpConnector:

    @staticmethod
    def run(config: ConfigModel, test: bool = False):
        log.info(f"SFTP connector activated")
        rsa_key = None
        if config.credentials is None:
            log.error("Missed credentials! Credentials required!")
            if not test:
                ErrorReporter.add(config.id, "Credentials required!")
                return False
            else:
                return {"error": True, "output": ""}
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if config.credentials.type == 'ssh-key':
            random_uuid = str(uuid.uuid4())
            log.info(f"Credentials type SSH Key")
            ConnectorManager.ssh_key_prepare(Decrypter.run(config.credentials.ssh_key), random_uuid)
            rsa_key = paramiko.RSAKey.from_private_key_file(f"{GlobalConfig.TEMP_DIR}/{random_uuid}.ssh.key")

        try:
            transport = paramiko.Transport((config.node.address, config.script.file_transfer.port))
            if rsa_key:
                log.debug("Connecting with SSH key")
                transport.connect(username=config.credentials.username, pkey=rsa_key)
            else:
                log.debug("Connecting with username/password")
                transport.connect(username=config.credentials.username,
                                  password=Decrypter.run(config.credentials.password))
            log.debug(f"Successfully connected")
            sftp = paramiko.SFTPClient.from_transport(transport)
            log.debug(f"Switched to SFTP")
        except Exception as e:
            ErrorReporter.add(config.id, f'Connection error!')
            ErrorReporter.add(config.id, f'Error: {e}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        try:
            file_attr = sftp.lstat(config.script.file_transfer.path)
            if stat.S_ISDIR(file_attr.st_mode):
                raise Exception("Path is directory! Exit")
            with sftp.open(config.script.file_transfer.path) as file:
                content = file.read()
            log.debug(f"File exists")

        except Exception as e:
            ErrorReporter.add(config.id, f'Read file error!')
            ErrorReporter.add(config.id, f'Error: {e}')

            if not test:
                ErrorReporter.add(config.id, "Config exit with error")
                return False
            else:
                return {"error": True, "output": ""}

        _content = Decoder.run(content)
        if _content is None:
            log.debug(f'Looks like content is binary file, cannot decode this data')
            if test:
                mime = magic.from_buffer(content, mime=True)
                return {"error": False, "output": None, "mime": mime}

        if test:
            return {"error": False, "output": _content}

        log.info("Add output to git")
        file = ConfigFile(content)
        config.status_ = True
        GitHandler.add(config, file)

        sftp.close()

        return True
