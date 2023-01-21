from typing import Union


class ConfigFile:

    _data: Union[bytes, None] = None
    _path: Union[str, None] = None

    def __init__(self, data: Union[bytes, None] = None):
        if data:
            self._data = data
        self._path = None

    @classmethod
    def data_from_str(cls, data: str) -> 'ConfigFile':
        return cls(data=data.encode())

    def save(self, path: str):
        if not path:
            raise Exception('Cannot save config file. Path does not set')
        self._path = path
        with open(path, 'wb') as f:
            f.write(self._data)
