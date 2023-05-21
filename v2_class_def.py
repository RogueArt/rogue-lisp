from bparser import BParser
from intbase import InterpreterBase

from v2_constants import *
import copy

class ClassDefinition:
    # constructor for a ClassDefinition
    def __init__(self, interpreter, interpreter_base: InterpreterBase, name, methods, fields, ancestor_class_defs):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.class_name = name
        self.methods = methods
        self.fields = fields
        self.ancestor_class_defs = ancestor_class_defs

    def set_methods(self, methods):
        self.methods = methods

    def set_fields(self, fields):
        self.fields = fields

    def set_ancestor_class_defs(self, ancestor_class_defs: list) -> None:
        self.ancestor_class_defs = ancestor_class_defs

    def get_ancestor_class_defs(self) -> List['ClassDefinition']:
        return self.ancestor_class_defs

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        from v2_object_def import ObjectDefinition
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, self.class_name,
                               copy.deepcopy(self.methods), copy.deepcopy(self.fields))
        return obj
