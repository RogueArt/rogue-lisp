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

    def create_obj(self):
        from v2_object_def import ObjectDefinition
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, self.class_name,
                               copy.deepcopy(self.methods), copy.deepcopy(self.fields))
        return obj

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        from v2_object_def import ObjectDefinition

        # Instantiate the ancestor list
        ancestors_objs: List[ObjectDefinition] = []
        for ancestor_class_def in self.ancestor_class_defs:
            ancestor_obj = ancestor_class_def.create_obj()
            ancestors_objs.append(ancestor_obj)
        
        # Create the object with the ancestor list
        obj = self.create_obj()
        obj.set_ancestor_objs(ancestors_objs)
        return obj
