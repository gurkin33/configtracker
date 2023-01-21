import os
import re
from os import environ
from os.path import isfile

from cryptography.fernet import Fernet


class Decrypter:

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    @staticmethod
    def run(data: str):
        key = environ.get('MASTER_KEY', None)
        if key is None:
            if isfile(f"{Decrypter.BASE_DIR}/../settings/master_key"):
                with open(f"{Decrypter.BASE_DIR}/../settings/master_key", 'r') as f:
                    key = f.read().strip()
            # key = getattr(config, 'MASTER_KEY') if hasattr(config, 'MASTER_KEY') else None
        if not key is None:
            try:
                token = re.search(r'fernet\((.*?)\)', data).group(1)
            except:
                token = data

            try:
                f = Fernet(key)
                return f.decrypt(token.encode()).decode('utf-8')
            except Exception as e:
                return data
        return data
