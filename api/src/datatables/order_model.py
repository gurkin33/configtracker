from typing import Literal
from pydantic import BaseModel


class OrderModel(BaseModel):
    column: int
    dir: Literal['asc', 'desc']
