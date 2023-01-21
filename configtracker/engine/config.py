from configtracker.engine.connectors import SshConnector, TelnetConnector, WgetConnector, FtpConnector, SftpConnector
from configtracker.engine.connectors.connector_manager import ConnectorManager
from configtracker.logger import Log2Variable, log
from configtracker.models.config import ConfigModel


class ConfigEngine(ConfigModel):

    def _choose_protocol(self):
        if self.script.type == 'expect':
            log.debug("Script type expect")
            if self.script.expect.protocol == 'ssh':
                log.debug("Script protocol ssh")
                return SshConnector
            elif self.script.expect.protocol == 'telnet':
                log.debug("Script protocol telnet")
                return TelnetConnector

        if self.script.type == 'wget':
            log.debug("Script type wget")
            return WgetConnector

        if self.script.type == 'file_transfer':
            log.debug("Script type file transfer")
            if self.script.file_transfer.protocol == 'ftp':
                log.debug("Script protocol ftp")
                return FtpConnector
            elif self.script.file_transfer.protocol == 'sftp':
                log.debug("Script protocol sftp")
                return SftpConnector

        return False

    def exec(self, test: bool = False):
        connector = self._choose_protocol()
        if test:
            Log2Variable.init()
        if not connector:
            ConnectorManager.disable_config_process(self.id)
            raise Exception(f'Unexpected script type: {self.script.type}')
        if test:
            return connector.run(self, test)
        else:
            connector.run(self)
            # print('Status: ', self.status_, self.id)
            if not self.status_:
                self.set_notification()
            ConnectorManager.set_config_status(self.id, self.status_)
            ConnectorManager.disable_config_process(self.id)
