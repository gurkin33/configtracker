from pydantic import BaseModel


class ScriptFileTransferModel(BaseModel):
    timeout: int = 10
    port: int = 22
    protocol: str = 'sftp'
    ftp_secure: bool = False
    path: str = ''
