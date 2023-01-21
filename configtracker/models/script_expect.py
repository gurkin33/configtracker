from typing import List
from pydantic import BaseModel
from configtracker.models.expectation import ExpectationModel


class ScriptExpectModel(BaseModel):
    timeout: int = 10
    protocol: str = 'ssh'
    port: int = 22
    username_prompt: List[str] = ['login as:', 'sername:']
    password_prompt: List[str] = ['assword:']
    default_prompt: List[str] = ['#', '>']
    expectations: List[ExpectationModel]