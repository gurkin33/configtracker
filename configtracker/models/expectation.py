from typing import List
from pydantic import BaseModel


class ExpectationModel(BaseModel):
    prompt: List[str] = ['#', '>', '>#']
    cmd: str
    timeout: int = 0
    save: bool = False
    secret: bool = False
    skip_top: int = 0
    skip_bottom: int = 0
