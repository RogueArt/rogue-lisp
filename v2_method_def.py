from typing import List

# TO-DO: Expose this globally through flag, not as variable
debug = 0
class MethodDefinition:
    def __init__(self, return_type: type, method_name: str, top_level_statement: list, parameter_names: List[str], parameter_types: List[type]):
        self.return_type: type = return_type
        self.method_name: str = method_name
        self.top_level_statement: list = top_level_statement
        self.parameter_names: List[str] = parameter_names
        self.parameter_types: List[type] = parameter_types

    # Top-level statement list in the form of nested lists
    def get_top_level_statement(self):
        return self.top_level_statement