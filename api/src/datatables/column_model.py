from types import NoneType
from typing import Union

from pydantic import BaseModel, validator
from api.src.datatables.search_model import SearchModel


class ColumnModel(BaseModel):
    name: str
    orderable: bool = False
    searchable: bool = False
    search: Union[SearchModel, NoneType] = None
