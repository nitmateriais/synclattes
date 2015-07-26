# -*- encoding: utf-8 -*-
# An implementation of views originally based on
# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views
# but extended to use the Table object instead of table.
# This allows to create materialized views with indexes in
# PostgreSQL, and also correctly implements schema support.
from sqlalchemy.sql.ddl import SchemaGenerator, SchemaDropper
from sqlalchemy import Table
from sqlalchemy.schema import DDLElement
from sqlalchemy.ext import compiler
from sqlalchemy.sql import table

class CreateView(DDLElement):
    def __init__(self, table):
        self.table = table

class DropView(DDLElement):
    def __init__(self, table):
        self.table = table

class RefreshMaterializedView(DDLElement):
    def __init__(self, table):
        self.table = table

def table_name(element, compiler):
    return compiler.sql_compiler.preparer.format_table(element.table)

@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return ' '.join(['CREATE'] + element.table._prefixes +
                    ['VIEW', table_name(element, compiler), 'AS',
                     compiler.sql_compiler.process(element.table.__view_selectable)])

@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return 'DROP VIEW ' + table_name(element, compiler)

@compiler.compiles(RefreshMaterializedView)
def compile(element, compiler, **kw):
    return 'REFRESH MATERIALIZED VIEW ' + table_name(element, compiler)

def gen_visit_view(self, table, create_ok=False,
                   include_foreign_key_constraints=None,
                   _is_metadata_operation=False):
    if not create_ok and not self._can_create_table(table):
        return

    table.dispatch.before_create(
        table, self.connection,
        checkfirst=self.checkfirst,
        _ddl_runner=self,
        _is_metadata_operation=_is_metadata_operation)

    for column in table.columns:
        if column.default is not None:
            self.traverse_single(column.default)

    self.connection.execute(CreateView(table))

    if hasattr(table, 'indexes'):
        for index in table.indexes:
            self.traverse_single(index)

    table.dispatch.after_create(
        table, self.connection,
        checkfirst=self.checkfirst,
        _ddl_runner=self,
        _is_metadata_operation=_is_metadata_operation)

SchemaGenerator.visit_view = gen_visit_view

def drop_visit_view(self, table, drop_ok=False, _is_metadata_operation=False):
    if not drop_ok and not self._can_drop_table(table):
        return

    table.dispatch.before_drop(
        table, self.connection,
        checkfirst=self.checkfirst,
        _ddl_runner=self,
        _is_metadata_operation=_is_metadata_operation)

    for column in table.columns:
        if column.default is not None:
            self.traverse_single(column.default)

    self.connection.execute(DropView(table))

    table.dispatch.after_drop(
        table, self.connection,
       checkfirst=self.checkfirst,
       _ddl_runner=self,
       _is_metadata_operation=_is_metadata_operation)

SchemaDropper.visit_view = drop_visit_view

def view(name, metadata, selectable, *args, **kwargs):
    t = Table(name, metadata, *args, **kwargs)
    t.__visit_name__ = 'view'
    t.__view_selectable = selectable
    for c in selectable.c:
        c.table = None
        t.append_column(c)
    return t
