import re
from os.path import isfile

from cryptography.fernet import Fernet
from os import environ
from api.config import GlobalConfig


class Encryptor:

    @staticmethod
    def run(data: str):
        key = environ.get('MASTER_KEY', None)
        try:
            data = re.search(r'fernet\((.*?)\)', data).group(1)
            if data:
                return data
        except:
            pass
        if key is None:
            if isfile(f"{GlobalConfig.SETTINGS_DIR}/master_key"):
                with open(f"{GlobalConfig.SETTINGS_DIR}/master_key", 'r') as f:
                    key = f.read().strip()
            # key = getattr(config, 'MASTER_KEY') if hasattr(config, 'MASTER_KEY') else None
        if key is not None:
            try:
                f = Fernet(key)
                return f"fernet({f.encrypt(data.encode()).decode('utf-8')})"
            except Exception as e:
                return data
        return data
