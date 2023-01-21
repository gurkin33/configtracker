from pydantic import BaseModel


class NodeModel(BaseModel):
    name: str
    address: str
