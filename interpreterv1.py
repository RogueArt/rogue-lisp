from typing import List, Dict
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint
import copy

# DEBUGGING ONLY - PLEASE DO NOT PUSH:


def get_sample_programs():
    return {
        'simple': ['(class main',
                   '(method hello_world (hi)',
                   '(begin',
                   '(print "Enter a number:")',
                   ')',
                   ')',
                   ')'],
        'single_class_multi_method': ['(class main',
                                      '(method main () (print "I am main!"))',
                                      '(method add (a b) (+ a b))',
                                      '(method sub (a b) (print "I am main!"))',
                                      ')'],
        'many_fields': ['(class main',
                        '(field foo_123 10)',
                        '(field name "unknown")',
                        '(field _awesome true)',
                        '(field obj_ref_field_puppy null)',
                        '(method main () (print "I am main!"))',
                        # '(method add (a b) (+ a b))',
                        ')'],
        # 'program2': ['(class main',
        #              '(field foo_123 10)',
        #              '(field name "unknown")',
        #              '(field _awesome true)',
        #              '(field obj_ref_field_puppy null)'
        #              '(field other null)',
        #              '(method hello_world () (print “hello world!”))',
        #              ')',
        #              '(class test',
        #              '(method hi () (print “hello world!”))',
        #              ')']
    }

# Deliberately small and obscure name for each easy debugging
# Will pritty print the array with the given indentation level


def fn(items, level=-1):
    for item in items:
        if isinstance(item, list):
            fn(item, level + 1)
        else:
            indentation = '    ' * level
            print('%s%s' % (indentation, item))


class MethodDefinition:
    def __init__(self, method_name: str, top_level_statement: list, parameters: List[str]):
        self.method_name = method_name
        self.top_level_statement = top_level_statement
        self.parameters = parameters
        pass

    # Returns the top-level statement list
    # TO-DO: Add a documentation for what this looks like
    def get_top_level_statement(self):
        return self.top_level_statement

    def get_num_parameters(self):
        return len(self.parameters)

    def get_parameter_names(self):
        return self.parameters

    def has_parameter(self, name: str) -> bool:
        return name in self.parameters


class ObjectDefinition:
    def __init__(self, _):
        pass

    # Interpret the specified method using the provided parameters
    def call_method(self, method_name, parameters):
        method = self.__find_method(method_name)
        statement = method.get_top_level_statement()
        result = self.__run_statement(statement)
        return result

    def __find_method(self, method_name):
        pass

    def __run_statement(self, statement):
        pass

    # runs/interprets the passed-in statement until completion and
    # gets the result, if any
    def __run_statement(self, statement):
        if self.is_a_print_statement(statement):
            result = self.__execute_print_statement(statement)
        elif self.is_an_input_statement(statement):
            result = self.__execute_input_statement(statement)
        elif self.is_a_call_statement(statement):
            result = self.__execute_call_statement(statement)
        elif self.is_a_while_statement(statement):
            result = self.__execute_while_statement(statement)
        elif self.is_an_if_statement(statement):
            result = self.__execute_if_statement(statement)
        elif self.is_a_return_statement(statement):
            result = self.__execute_return_statement(statement)
        elif self.is_a_begin_statement(statement):
            result = self.__execute_all_sub_statements_of_begin_statement(
                statement)
        return result

    def is_a_print_statement(self, statement):
        return False

    def is_an_input_statement(self, statement):
        return False

    def is_a_call_statement(self, statement):
        return False

    def is_a_while_statement(self, statement):
        return False

    def is_an_if_statement(self, statement):
        return False

    def is_a_return_statement(self, statement):
        return False

    def is_a_begin_statement(self, statement):
        return False

    def __execute_print_statement(self, statement):
        pass

    def __execute_input_statement(self, statement):
        pass

    def __execute_call_statement(self, statement):
        pass

    def __execute_while_statement(self, statement):
        pass

    def __execute_if_statement(self, statement):
        pass

    def __execute_return_statement(self, statement):
        pass

    def __execute_all_sub_statements_of_begin_statement(self, statement):
        pass


class ClassDefinition:
    # constructor for a ClassDefinition
    def __init__(self, name, methods, fields):
        self.name = name
        self.methods = methods
        self.fields = fields

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        obj = ObjectDefinition()
        for method in self.methods:
            obj.add_method(method)
        for field in self.fields:
            obj.add_field(field.name(), field.initial_value())
        return obj


class Interpreter(InterpreterBase):
    def __init__(self, console_ouptput=True, trace_output=False):
        # call InterpreterBase's constructor
        super().__init__(console_ouptput, trace_output)

        self.class_definitions = dict()
        self.objects = dict()

    def run(self, program):
        # Parse the program into a more easily processed form
        result, parsed_program = BParser.parse(program)
        if result == False:
            print('Parsing failed. Please check the input file.')
            return
        else:
            # pprint(parsed_program)
            fn(parsed_program)

        # TO-DO: Add parsing for classes
        self.__discover_all_classes_and_track_them(parsed_program)
        class_def = self.__find_definition_for_class("main")

        # obj = class_def.instantiate_object()
        # obj.run_method("main")

    def __discover_all_classes_and_track_them(self, parsed_program):
        # Add classes to the list
        for class_def in parsed_program:
            # Get class name
            class_name = class_def[1]

            # Parse the methods and fields from the object
            methods = self.__get_methods_for_class(class_def)
            fields = self.__get_fields_for_class(class_def)

            # Create a new class with given methods and fields
            self.class_definitions[class_name] = ClassDefinition(
                class_name, methods, fields)

    def __get_methods_for_class(self, class_def: list) -> list:
        methods = {}
        for statement in class_def[2:]:
            if statement[0] == Interpreter.METHOD_DEF:
                # Each method is in this format:
                # ['method', <name>, [<parameters>], [<statements>]]
                method_name: str = statement[1]
                parameters_list: List[str] = statement[2]
                top_level_statement = statement[3]

                # Methods map stores <name:MethodDefinition> pairs
                methods[method_name] = MethodDefinition(
                    method_name, top_level_statement, parameters_list)
        return methods

    def __get_fields_for_class(self, class_def: list) -> list:
        fields = {}
        for statement in class_def[2:]:
            if statement[0] == Interpreter.FIELD_DEF:
                field_name: str = statement[1]
                value: List[str] = self.__parse_str_into_python_value(
                    statement[2])

                # Fields map stores <name:value> pairs
                fields[field_name] = value

        return fields

    def __find_definition_for_class(self, class_name: str):
        return self.class_definitions[class_name]

    def __parse_str_into_python_value(self, value: str):
        if value == InterpreterBase.TRUE_DEF:
            return True
        elif value == InterpreterBase.FALSE_DEF:
            return False
        elif value == InterpreterBase.NULL_DEF:
            return None
        elif value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        else:
            return int(value)


# CODE FOR DEBUGGING PURPOSES ONLY
if __name__ == "__main__":
    # file_name = './examples/example1.txt'
    # program = [line.strip() for line in open(file_name)]
    programs = get_sample_programs()
    program = programs['many_fields']

    interpreter = Interpreter()
    interpreter.run(program)
