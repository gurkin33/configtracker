from pydantic import BaseModel
from configtracker.models.script_expect import ScriptExpectModel
from configtracker.models.script_wget import ScriptWgetModel
from configtracker.models.script_file_transfer import ScriptFileTransferModel


class ScriptModel(BaseModel):
    name: str = ''
    type: str = ''
    wget: ScriptWgetModel = None
    expect: ScriptExpectModel = None
    file_transfer: ScriptFileTransferModel = None
