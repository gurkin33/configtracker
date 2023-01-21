from types import NoneType
from typing import List
from pydantic import BaseModel
from configtracker.models.node import NodeModel
from configtracker.models.script import ScriptModel
from configtracker.models.credentials import CredentialsModel


class ConfigModel(BaseModel):

    name: str
    id: str = None
    repo_id: str = None
    node: NodeModel
    emails: List[str] = []
    script: ScriptModel
    credentials: CredentialsModel | NoneType
    status_: bool = False

    _notifications = {
        # configs - {"config_id": config}
        "configs": {

        },
        # emails - {"email": "success": [config_id list], "fail": [config_id list] }
        "emails": {

        }
    }

    def set_notification(self):
        # log.debug("Set notifications")
        print('Notification Emails: ', self.emails)
        print('Notification s: ', self.status_, self.id)
        if not self.emails:
            return

        self._notifications["configs"][self.id] = self

        for email in self.emails:
            if self._notifications["emails"].get(email, None) is None:
                self._notifications["emails"][email] = {"success": [], "fail": []}

            if self.status_:
                self._notifications["emails"][email]["success"].append(self.id)
            else:
                self._notifications["emails"][email]["fail"].append(self.id)
        # print('Notifications: ', self._notifications)

    @classmethod
    def get_notifications(cls):
        return cls._notifications
