from typing import Any, List

from respect_validation import FormValidator, Validator as v


class DatatablesValidator:

    @staticmethod
    def _get_rules(columns: List):
        return {
            "draw": v.anyOf(v.NoneType(), v.intType().min(0)),
            "start": v.anyOf(v.NoneType(), v.intType().min(0)),
            "length": v.anyOf(v.NoneType(), v.intType().min(0)),
            "search": v.anyOf(v.NoneType(), v.keySet(
                v.key("value", v.stringType()),
                v.key("value2", v.stringType()),
                v.key("condition", v.include([
                    'equals', 'contains', 'starts_with', 'ends_with',
                    'less_than', 'greater_then'
                ]))
            )),
            "order": v.anyOf(v.NoneType(), v.listType().length(min_value=1).each(v.keySet(
                v.key("column", v.intType().min(0)),
                v.key("dir", v.stringType().include(['asc', 'desc']))
            ))),
            "columns": v.listType().length(min_value=1).each(v.keySet(
                v.key("name", v.stringType().include_columns(columns)),
                v.key("searchable", v.boolType(), False),
                v.key("orderable", v.boolType(), False),
                v.key("search", v.anyOf(v.NoneType(), v.dictType().keySet(
                    v.key("value", v.stringType()),
                    v.key("value2", v.stringType()),
                    v.key("condition", v.include([
                        'equals', 'contains', 'starts_with', 'ends_with',
                        'less_than', 'greater_then'
                    ]))
                )), False)
            ))
        }

    @staticmethod
    def _get_columns(model: Any):
        columns = model.__table__.columns.keys()
        if hasattr(model, 'references') and len(model.references):
            columns.append('references')
        if hasattr(model, 'additional_table_columns') and len(model.additional_table_columns):
            columns = columns + model.additional_table_columns
        return columns

    @classmethod
    def fv(cls) -> 'FormValidator':
        return FormValidator()

    @classmethod
    def validate(cls, params, model: Any):
        return cls.fv().validate(params, cls._get_rules(cls._get_columns(model)))
