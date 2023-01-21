from types import NoneType
from typing import List, Union
from pydantic import BaseModel

from api.src.datatables.column_model import ColumnModel
from api.src.datatables.order_model import OrderModel
from api.src.datatables.search_model import SearchModel


class DataTablesModel(BaseModel):
    columns: List[ColumnModel]
    order: List[OrderModel] = []
    search: Union[SearchModel, NoneType] = None
    start: int = 0
    length: int = 10
    draw: int = 0
