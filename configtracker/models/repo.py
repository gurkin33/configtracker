from typing import List
from pydantic import BaseModel
from configtracker.engine.config import ConfigEngine


class RepoModel(BaseModel):
    name: str
    id: str
    configs: List[ConfigEngine]
