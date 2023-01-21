from configtracker import log


class Decoder:

    encodings = ['utf-8', 'windows-1250', 'windows-1252']

    @classmethod
    def run(cls, data):
        content = None
        for e in cls.encodings:
            try:
                content = data.decode(e)
            except UnicodeDecodeError:
                log.debug(f'Encoding {e} is not supported')
            else:
                log.debug(f'Used encoding {e}')
                break
        return content
