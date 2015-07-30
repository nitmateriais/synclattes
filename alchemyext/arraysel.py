from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ARRAY

class ArraySel(ColumnElement):
    def __init__(self, select):
        select = select.as_scalar()
        self.select = select
        self.type = ARRAY(select.type)

@compiles(ArraySel)
def visit_array_sel(element, compiler, **kw):
    return "ARRAY" + compiler.process(element.select)
