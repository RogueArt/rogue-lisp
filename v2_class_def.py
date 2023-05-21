from bparser import BParser
from intbase import InterpreterBase

from v2_constants import *
import copy

class ClassDefinition:
    # constructor for a ClassDefinition
    def __init__(self, interpreter, interpreter_base: InterpreterBase, name, methods, fields, ancestors = []):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.class_name = name
        self.methods = methods
        self.fields = fields
        self.ancestors = ancestors

    def set_methods(self, methods):
        self.methods = methods

    def set_fields(self, fields):
        self.fields = fields

    def set_ancestors(self, ancestors: list) -> None:
        self.ancestors = ancestors

    def get_ancestors(self) -> List['ClassDefinition']:
        return self.ancestors
    
    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        from v2_object_def import ObjectDefinition
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, self.class_name,
                               copy.deepcopy(self.methods), copy.deepcopy(self.fields))
        return obj
