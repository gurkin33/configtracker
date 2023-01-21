from pydantic import BaseModel


class CredentialsModel(BaseModel):
    username: str
    password: str
    ssh_key: str
    type: str
