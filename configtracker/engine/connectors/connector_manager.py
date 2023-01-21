import glob
from datetime import datetime
from os import path, stat, chmod, remove
from mini_app import app
from api.src.models.config import ConfigModel
from api.config import GlobalConfig


class ConnectorManager:

    @staticmethod
    def set_config_status(config_id: str, status: bool = False):
        with app.app_context():
            config = ConfigModel.find_by_id(config_id)
            if config:
                config.status = status
                config.save()

    @staticmethod
    def disable_config_process(config_id: str):
        with app.app_context():
            ConfigModel.set_in_process(config_id=config_id)

    @staticmethod
    def set_config_properties():
        list_of_files = filter(path.isfile,
                               glob.glob(GlobalConfig.REPOS_ROOT_PATH + '/**/*', recursive=True))
        configs = []
        for file in list_of_files:
            if file.endswith('.lnk'):
                continue
            configs.append([
                file.split('/')[-1],
                stat(file).st_size,
                datetime.utcfromtimestamp(stat(file).st_mtime),
            ])
        if configs:
            with app.app_context():
                ConfigModel.set_config_properties(configs)

    @staticmethod
    def ssh_key_prepare(key: str, random_uuid: str):
        f = open(f"{GlobalConfig.TEMP_DIR}/{random_uuid}.ssh.key", "w")
        f.write(key + "\n")
        f.close()
        chmod(f"{GlobalConfig.TEMP_DIR}/{random_uuid}.ssh.key", 0o600)

    @staticmethod
    def remove_all_ssh_keys():
        for f in glob.glob(f"{GlobalConfig.TEMP_DIR}/*.ssh.key"):
            remove(f)

