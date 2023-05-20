from typing import List

# TO-DO: Expose this globally through flag, not as variable
debug = 0
class MethodDefinition:
    def __init__(self, method_name: str, top_level_statement: list, parameter_names: List[str]):
        self.method_name = method_name
        self.top_level_statement = top_level_statement
        self.parameter_names = parameter_names

    # Top-level statement list in the form of nested lists
    def get_top_level_statement(self):
        return self.top_level_statement