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
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, self.class_name, self,
                               copy.deepcopy(self.methods), copy.deepcopy(self.fields))
        return obj

    def __get_lowest_common_ancestor(self, other_class_def):
        base_ancestors = [self] + self.ancestor_class_defs
        other_ancestors = [other_class_def] + other_class_def.ancestor_class_defs

        # Gets LCA between the two lists
        for base_ancestor in base_ancestors:
            for other_ancestor in other_ancestors:
                if base_ancestor.class_name == other_ancestor.class_name:
                    return base_ancestor

    def is_other_class_def_same_or_derived_class(self, other_class_def):
        # Check if both classes are the same
        lhs_and_rhs_are_same = self.class_name == other_class_def.class_name
        if lhs_and_rhs_are_same:
            return True
        
        # Check if base or derived classes now
        # No LCA - then these classes do not share ancestors
        lowest_common_ancestor = self.__get_lowest_common_ancestor(other_class_def)
        if lowest_common_ancestor is None:
            return False

        # Two rules must stand for the RHS to be more derived than LHS
        # 1. The LHS must be the LCA - if it's not, then this is a sibling class
        # 2. The RHS must not be the LCA while LHS is not LCA - this implies that that would be the more base class
        lhs_is_lca = lowest_common_ancestor.class_name == self.class_name
        rhs_is_not_lca = lowest_common_ancestor.class_name != other_class_def.class_name
        return lhs_and_rhs_are_same or (lhs_is_lca and rhs_is_not_lca)

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        from v2_object_def import ObjectDefinition

        # Instantiate the ancestor list
        """
        Explanation of algorithm:
        Let's say we have three classes: A -> B -> C
        
        Our code needs to read in class defs in the order of C <- B <- A
        Then in order for ancestors to have access to above ancestors, we do this:
        1. Read in the class defs in reverse order (A, B, C)
        2. Upon initializing each ancestor, copy over the list of current so far, then add to list

        Example:
        Once we read in A, then instantiate this object, set ancestors (which are `[]`), then add to list
        Once we read in B, then instantiate this object, set ancestors (which are `[A]`), then add to list
        
        Each time, we reverse this list (though we don't have to), since it makes it easy for us to do:
        for ancestor in ancestors in Python, without having to remember to reverse iterate the list each time
        """
        ancestors_objs: List[ObjectDefinition] = []
        for ancestor_class_def in self.ancestor_class_defs[::-1]:
            ancestor_obj = ancestor_class_def.create_obj()
            ancestor_obj.set_ancestor_objs(copy.copy(ancestors_objs[::-1]))
            ancestors_objs.append(ancestor_obj)
        
        # Create the object with the ancestor list
        obj = self.create_obj()
        obj.set_ancestor_objs(ancestors_objs[::-1])
        return obj
