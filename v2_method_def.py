from typing import List
from v2_constants import *

class MethodDefinition:
    def __init__(self, return_type: type | None, method_name: str, top_level_statement: list, parameter_names: List[str], parameter_types: List[type]):
        self.return_type: type | None = return_type
        self.method_name: str = method_name
        self.top_level_statement: list = top_level_statement
        self.parameter_names: List[str] = parameter_names
        self.parameter_types: List[type] = parameter_types

    # Top-level statement list in the form of nested lists
    def get_top_level_statement(self):
        return self.top_level_statement
    
    # PROBLEM 4: RETURN TYPES
    def check_return_type_compatibility(self, final_result_program_value) -> bool:
        from v2_class_def import ClassDefinition
        # Case 1: Function is of type void
        if self.return_type is None:
            return final_result_program_value is None

        # Case 2: Primitives - we just need to know if they are the same type
        if self.return_type in [int, str, bool] or final_result_program_value.type() in [int, str, bool]:
            return self.return_type is final_result_program_value.type()
        
        # Case 3: Both are object references
        # TO-DO: Update this for polymorphism
        if isinstance(self.return_type, ClassDefinition) and isinstance(final_result_program_value.type(), ClassDefinition):
            return self.return_type.class_name == final_result_program_value.type().class_name

        # Case 4: One is an object reference, the other is a dangling null
        if isinstance(self.return_type, ClassDefinition) and final_result_program_value.type() is None:
            return True

        # TO-DO: Maybe throw an error here?
        return False

    def get_default_value_by_return_type(self):
        from v2_class_def import ClassDefinition

        return_type = self.return_type
        if return_type is int:
            return 0
        elif return_type is str:
            return ''
        elif return_type is bool:
            return False
        # Case where we return a null, but know Object type
        elif isinstance(return_type, ClassDefinition):
            return None
        # Void type - we expect this case to be never called
        else:
            return None