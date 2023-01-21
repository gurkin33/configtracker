import re

from flask_sqlalchemy import DefaultMeta
from sqlalchemy import func, and_, or_, cast
from api.db import TableModel, db
from api.src.datatables.datatables_model import DataTablesModel


class DataTables:

    def __init__(self, params, model: TableModel):
        self.dt = DataTablesModel(**params)
        self.model = model
        self.requested_columns = []
        self.references = None
        self.total = 0
        self.total_filtered = 0
        self.search_or = None
        self.search_and = None

    def _init_query(self):
        return db.session.query(self.model)

    def _init_references(self):
        if self.model.references:
            for rs in self.model.references:
                # print(type(rs['ref_model']))
                # print(type(rs['ref_model']) == DefaultMeta)
                if self.references is None:
                    if type(rs['ref_model']) == DefaultMeta:
                        self.references = func.coalesce(func.count(getattr(rs['ref_model'], rs['ref_model_id'])), 0)
                    else:
                        self.references = func.coalesce(func.count(getattr(rs['ref_model'].c, rs['ref_model_id'])), 0)
                    continue
                else:
                    if type(rs['ref_model']) == DefaultMeta:
                        self.references += func.coalesce(func.count(getattr(rs['ref_model'], rs['ref_model_id'])), 0)
                    else:
                        self.references += func.coalesce(func.count(getattr(rs['ref_model'].c, rs['ref_model_id'])), 0)

    def _set_references(self):
        query = db.session.query(
            self.model,
            self.references.label("references")
        )
        for r in self.model.references:
            if type(r['ref_model']) == DefaultMeta:
                query = query.outerjoin(r['ref_model'], and_(
                        getattr(r['ref_model'], r['ref_model_id']) == getattr(self.model, r["self_id"])))
            else:
                query = query.outerjoin(r['ref_model'], and_(
                        getattr(r['ref_model'].c, r['ref_model_id']) == getattr(self.model, r["self_id"])))
        return query.group_by(getattr(self.model, r["self_id"]))

    def _set_global_filter(self):
        search = []
        for c in self.dt.columns:
            if c.name == "references" or not c.searchable or c.name in self.model.relationships:
                continue
            if self.dt.search.condition == 'equals' and \
                    self._check_column_type(getattr(self.model, c.name), ['UUID', 'VARCHAR', 'INT']):
                if str(getattr(self.model, c.name).type) == 'UUID':
                    search.append(cast(getattr(self.model, c.name), db.String) == self.dt.search.value)
                else:
                    search.append(getattr(self.model, c.name) == self.dt.search.value)
            if self.dt.search.condition == 'not_equals' and \
                    self._check_column_type(getattr(self.model, c.name), ['UUID', 'VARCHAR', 'INT']):
                if str(getattr(self.model, c.name).type) == 'UUID':
                    search.append(cast(getattr(self.model, c.name), db.String) != self.dt.search.value)
                else:
                    search.append(getattr(self.model, c.name) != self.dt.search.value)
            if self.dt.search.condition == 'contains' and \
                    self._check_column_type(getattr(self.model, c.name), ['UUID', 'VARCHAR']):
                if str(getattr(self.model, c.name).type) == 'UUID':
                    search.append(cast(getattr(self.model, c.name), db.String).like(f'%{self.dt.search.value}%'))
                else:
                    search.append(getattr(self.model, c.name).like(f'%{self.dt.search.value}%'))
            if self.dt.search.condition == 'not_contains' and \
                    self._check_column_type(getattr(self.model, c.name), ['UUID', 'VARCHAR']):
                if str(getattr(self.model, c.name).type) == 'UUID':
                    search.append(cast(getattr(self.model, c.name), db.String).nolike(f'%{self.dt.search.value}%'))
                else:
                    search.append(getattr(self.model, c.name).nolike(f'%{self.dt.search.value}%'))
            if self.dt.search.condition == 'starts_with' and \
                    self._check_column_type(getattr(self.model, c.name), ['UUID', 'VARCHAR']):
                if str(getattr(self.model, c.name).type) == 'UUID':
                    search.append(cast(getattr(self.model, c.name), db.String).like(f'{self.dt.search.value}%'))
                else:
                    search.append(getattr(self.model, c.name).like(f'{self.dt.search.value}%'))
            if self.dt.search.condition == 'ends_with' and \
                    self._check_column_type(getattr(self.model, c.name), ['UUID', 'VARCHAR']):
                if str(getattr(self.model, c.name).type) == 'UUID':
                    search.append(cast(getattr(self.model, c.name), db.String).like(f'%{self.dt.search.value}'))
                else:
                    search.append(getattr(self.model, c.name).like(f'%{self.dt.search.value}'))
            if self.dt.search.condition == 'less_than' and \
                    self._check_column_type(getattr(self.model, c.name), ['INT', 'TIMESTAMP']):
                search.append(getattr(self.model, c.name) < self.dt.search.value)
            if self.dt.search.condition == 'great_than' and \
                    self._check_column_type(getattr(self.model, c.name), ['INT', 'TIMESTAMP']):
                search.append(getattr(self.model, c.name) > self.dt.search.value)
            if self.dt.search.condition == 'between' and \
                    self._check_column_type(getattr(self.model, c.name), ['INT', 'TIMESTAMP']):
                search.append(getattr(self.model, c.name).between(self.dt.search.value, self.dt.search.value2))
        if len(search):
            self.search_or = or_(*search)

    def _set_column_filter(self):
        search = []
        for c in self.dt.columns:
            if c.name == "references" or not c.searchable or \
                    c.name in self.model.relationships or c.search is None:
                continue
            if c.search.condition == 'equals' and \
                    self._check_column_type(getattr(self.model, c.name), ['VARCHAR', 'INT']):
                search.append(getattr(self.model, c.name) == c.search.value)
            if c.search.condition == 'not_equals' and \
                    self._check_column_type(getattr(self.model, c.name), ['VARCHAR', 'INT']):
                search.append(getattr(self.model, c.name) != c.search.value)
            if c.search.condition == 'contains' and \
                    self._check_column_type(getattr(self.model, c.name), ['VARCHAR']):
                search.append(getattr(self.model, c.name).like(f'%{c.search.value}%'))
            if c.search.condition == 'not_contains' and \
                    self._check_column_type(getattr(self.model, c.name), ['VARCHAR']):
                search.append(getattr(self.model, c.name).nolike(f'%{c.search.value}%'))
            if c.search.condition == 'starts_with' and \
                    self._check_column_type(getattr(self.model, c.name), ['VARCHAR']):
                search.append(getattr(self.model, c.name).like(f'{c.search.value}%'))
            if c.search.condition == 'ends_with' and \
                    self._check_column_type(getattr(self.model, c.name), ['VARCHAR']):
                search.append(getattr(self.model, c.name).like(f'%{c.search.value}'))
            if c.search.condition == 'less_than' and \
                    self._check_column_type(getattr(self.model, c.name), ['INT', 'TIMESTAMP']):
                search.append(getattr(self.model, c.name) < c.search.value)
            if c.search.condition == 'great_than' and \
                    self._check_column_type(getattr(self.model, c.name), ['INT', 'TIMESTAMP']):
                search.append(getattr(self.model, c.name) > c.search.value)
            if c.search.condition == 'between' and \
                    self._check_column_type(getattr(self.model, c.name), ['INT', 'TIMESTAMP']):
                search.append(getattr(self.model, c.name).between(c.search.value, c.search.value2))

        if len(search):
            self.search_and = and_(*search)

    def _set_order(self, query):
        order_by = []
        if len(self.dt.order):
            # print(self.dt.order)
            for o in self.dt.order:
                if not self.dt.columns[o.column].orderable \
                        or self.dt.columns[o.column].name in self.model.not_sortable \
                        or self.dt.columns[o.column].name in self.model.relationships:
                    continue
                if self.dt.columns[o.column].name == 'references':
                    continue
                if o.dir == 'asc':
                    order_by.append(getattr(self.model, self.dt.columns[o.column].name))
                else:
                    order_by.append(getattr(self.model, self.dt.columns[o.column].name).desc())
        if len(order_by):
            # print(order_by)
            return query.order_by(*order_by)
        return query

    def _set_pagination(self, query):
        return query.offset(self.dt.start).limit(self.dt.length)

    def result(self):
        self._init_references()
        if self.references is not None:
            query = self._set_references()
        else:
            query = self._init_query()
        query = self.after_query_init(query)
        self.total = query.count()
        if self.dt.search:
            self._set_global_filter()
        self._set_column_filter()

        if self.search_and is not None and self.search_or is not None:
            query = query.filter(and_(self.search_and, self.search_or))
        if self.search_and is not None and self.search_or is None:
            query = query.filter(self.search_and)
        if self.search_and is None and self.search_or is not None:
            query = query.filter(self.search_or)
        self.total_filtered = query.count()
        query = self._set_order(query)
        # print(query)
        if self.dt.length:
            query = self._set_pagination(query)
        return query

    @staticmethod
    def _check_column_type(column, types):
        column_type = re.sub(r'\(\d+\)', '', str(column.type))
        return column_type in types

    @staticmethod
    def after_query_init(query):
        return query


