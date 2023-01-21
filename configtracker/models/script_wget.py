from pydantic import BaseModel


class ScriptWgetModel(BaseModel):
    timeout: int = 10
    link: str = ''
