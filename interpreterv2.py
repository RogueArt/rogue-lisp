from typing import List, Dict, Union
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint
import copy

from v2_method_def import *
# from v2_class_def import ClassDefinition
from v2_object_def import ObjectDefinition, ClassDefinition, ValueHelper
# from v2_value_def import ValueHelper

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

    # Parameters list comes in as [type_str, argument_name], we need to convert this to a list of types
    def __parse_expected_types_from_parameters_list(self, params_list: List[List[str]]) -> List[type]:
        return [ValueHelper.get_variable_type_from_type_str(self, param_type) for param_type, _ in params_list]

    def __parse_parameter_names_from_parameters_list(self, params_list: List[List[str]]) -> List[str]:
        return [param[1] for param in params_list]

    def __get_methods_for_class(self, class_def: list) -> list:
        methods = {}
        for statement in class_def[2:]:
            if statement[0] == Interpreter.METHOD_DEF:
                # Each method is in this format:
                # ['method', <return type>, <name>, [<parameters>], [<statements>]]
                return_type_str: str = statement[1]
                method_name: str = statement[2]
                parameters_list: List[str] = statement[3]
                top_level_statement = statement[4]
                
                return_type = ValueHelper.get_return_type_from_type_str(self, return_type_str)
                parameter_names = self.__parse_parameter_names_from_parameters_list(parameters_list)
                parameter_types = self.__parse_expected_types_from_parameters_list(parameters_list)

                # Duplicate method names are not allowed
                if method_name in methods:
                    self.interpreter_base.error(ErrorType.NAME_ERROR)

                # Methods map stores <name:MethodDefinition> pairs
                methods[method_name] = MethodDefinition(return_type, method_name, top_level_statement, parameter_names, parameter_types)
        return methods

    def __get_fields_for_class(self, class_def: list) -> list:
        fields = {}
        for statement in class_def[2:]:
            if statement[0] == Interpreter.FIELD_DEF:
                field_type_str: str = statement[1]
                field_name: str = statement[2]
                value_str: str = statement[3]

                # Duplicate field names are not allowed
                if field_name in fields:
                    self.interpreter_base.error(ErrorType.NAME_ERROR)

                # Read the type hint and value, verify that they match
                value: int|bool|str|None|ObjectDefinition = ValueHelper.parse_str_into_python_value(value_str)
                field_type: type = ValueHelper.get_variable_type_from_type_str(self, field_type_str)
                if not ValueHelper.is_value_compatible_with_type(value, field_type):
                    self.interpreter_base.error(ErrorType.TYPE_ERROR)
                
                # TO-DO: Add variable types
                # Fields map stores <name:Value> pairs
                fields[field_name] = { 'type': field_type, 'value': value }

        return fields

    def find_definition_for_class(self, class_name: str):
        # Check if class exists
        if class_name in self.class_definitions:
            return self.class_definitions[class_name]
        
        # If not found, then throw an error for trying to get invalid class
        self.interpreter_base.error(ErrorType.TYPE_ERROR)

# CODE FOR DEBUGGING PURPOSES ONLY
if __name__ == "__main__":
    from manual_testing_v2 import get_test_programs, fn

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

    test_programs = get_test_programs()
    skip_tests = []  # , 'set_fields'
    # skip_tests = ['field_and_method_types']
    run_tests = ['call_with_valid_default_types']
    # run_tests = ['test_set_instantiation', 'test_return_instantiation', 'test_null_return_instantiation'] 
    for count, (program_name, program) in enumerate(test_programs.items()):
        if (len(run_tests) > 0 and program_name not in run_tests) or program_name in skip_tests:
            print(YELLOW + f"Skipping test #{count+1} {program_name}" + RESET)
            continue

        if (len(run_tests) > 0 and program_name in run_tests) or len(run_tests) == 0:
            try:
                print(GREEN + f"Running test #{count+1} {program_name}:" + RESET)
                interpreter = Interpreter()
                interpreter.run(program)
                print(GREEN + f"Finished testing {program_name}\n\n" + RESET)
            except RuntimeError as e:
                if e.args[0] == 'ErrorType.TYPE_ERROR':
                    print("Code exited with ErrorType.TYPE_ERROR")
                elif e.args[0] == 'ErrorType.NAME_ERROR':
                    print("Code exited with ErrorType.NAME_ERROR")
                elif e.args[0] == 'ErrorType.SYNTAX_ERROR':
                    print("Code exited with ErrorType.SYNTAX_ERROR")
                elif e.args[0] == 'ErrorType.FAULT_ERROR':
                    print("Code exited with ErrorType.FAULT_ERROR")
                else:
                    raise e
