from typing import Literal
from pydantic import BaseModel


class SearchModel(BaseModel):
    value: str = ''
    value2: str = ''
    condition: Literal[
        'equals',
        'not_equals',
        'contains',
        'not_contains',
        'starts_with',
        'ends_with',
        'less_than',
        'greater_than',
        'between'
    ]
