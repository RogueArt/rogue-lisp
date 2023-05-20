from typing import List, Dict, Union
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint
import copy

from v2_method_def import *
from v2_class_def import ClassDefinition
from v2_object_def import ObjectDefinition
from v2_value_def import ValueHelper

class Interpreter(InterpreterBase):
    def __init__(self, console_ouptput=True, inp=None, trace_output=False):
        # call InterpreterBase's constructor
        super().__init__(console_ouptput, inp)

        self.interpreter_base = super()
        self.class_definitions = dict()
        self.objects = dict()

    def run(self, program):
        # Parse the program into a more easily processed form
        result, parsed_program = BParser.parse(program)
        if result == False:
            print('Parsing failed. Please check the input file.')
            return
        else:
            if (debug >= 2):
                fn(parsed_program)
            pass

        # TO-DO: Add parsing for classes
        self.__discover_all_classes_and_track_them(parsed_program)
        class_def = self.find_definition_for_class(InterpreterBase.MAIN_CLASS_DEF)
        obj = class_def.instantiate_object()
        obj.call_method(InterpreterBase.MAIN_FUNC_DEF, {})

    def __discover_all_classes_and_track_them(self, parsed_program):
        # Add classes to the list
        for class_def in parsed_program:
            # Get class name
            class_name = class_def[1]

            # Duplicate class definitions are not allowed
            if class_name in self.class_definitions:
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Parse the methods and fields from the object
            methods = self.__get_methods_for_class(class_def)
            fields = self.__get_fields_for_class(class_def)

            # Create a new class with given methods and fields
            self.class_definitions[class_name] = ClassDefinition(
                self, self.interpreter_base, class_name, methods, fields)

    def __get_methods_for_class(self, class_def: list) -> list:
        methods = {}
        for statement in class_def[2:]:
            if statement[0] == Interpreter.METHOD_DEF:
                # Each method is in this format:
                # ['method', <name>, [<parameters>], [<statements>]]
                method_name: str = statement[1]
                parameters_list: List[str] = statement[2]
                top_level_statement = statement[3]
                
                # Duplicate method names are not allowed
                if method_name in methods:
                    self.interpreter_base.error(ErrorType.NAME_ERROR)

                # Methods map stores <name:MethodDefinition> pairs
                methods[method_name] = MethodDefinition(
                    method_name, top_level_statement, parameters_list)
        return methods

    def __get_fields_for_class(self, class_def: list) -> list:
        fields = {}
        for statement in class_def[2:]:
            if statement[0] == Interpreter.FIELD_DEF:
                field_name: str = statement[1]

                # Duplicate field names are not allowed
                if field_name in fields:
                    self.interpreter_base.error(ErrorType.NAME_ERROR)

                value: List[str] = ValueHelper.parse_str_into_python_value(statement[2])

                # Fields map stores <name:value> pairs
                fields[field_name] = value

        return fields

    def find_definition_for_class(self, class_name: str):
        # Check if class exists
        if class_name in self.class_definitions:
            return self.class_definitions[class_name]
        
        # If not found, then throw an error for trying to get invalid class
        self.interpreter_base.error(ErrorType.TYPE_ERROR)

# CODE FOR DEBUGGING PURPOSES ONLY
if __name__ == "__main__":
    from testing import get_test_programs, fn

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

    test_programs = get_test_programs()
    # skip_tests = ['set_fields']  # , 'set_fields'
    skip_tests = []
    run_tests = []
    # run_tests = ['test_set_instantiation', 'test_return_instantiation', 'test_null_return_instantiation'] 
    for count, (program_name, program) in enumerate(test_programs.items()):
        if (len(run_tests) > 0 and program_name not in run_tests) or program_name in skip_tests:
            print(YELLOW + f"Skipping test #{count+1} {program_name}" + RESET)
            continue

        if (len(run_tests) > 0 and program_name in run_tests) or len(run_tests) == 0:
            print(GREEN + f"Running test #{count+1} {program_name}:" + RESET)
            interpreter = Interpreter()
            interpreter.run(program)
            print(GREEN + f"Finished testing {program_name}\n\n" + RESET)
