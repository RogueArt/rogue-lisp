from intbase import InterpreterBase, ErrorType
from bparser import BParser


class ObjectDefinition:
    def __init__(self, _):
        pass

    # Interpret the specified method using the provided parameters
    def call_method(self, method_name, parameters):
        method = self.__find_method(method_name)
        statement = method.get_top_level_statement()
        result = self.__run_statement(statement)
        return result

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


class ClassDefinition:
    # constructor for a ClassDefinition
    def __init__(self, _):
        pass

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        obj = ObjectDefinition()
        for method in self.my_methods:
            obj.add_method(method)
        for field in self.my_fields:
            obj.add_field(field.name(), field.initial_value())
        return obj


class Interpreter(InterpreterBase):
    def __init__(self, console_ouptput=True, trace_output=False):
        # call InterpreterBase's constructor
        super().__init__(console_ouptput, trace_output)

    def run(self, program):
        # Parse the program into a more easily processed form
        result, parsed_program = BParser.parse(program)
        if result == False:
            return  # error
        self.__discover_all_classes_and_track_them(parsed_program)
        class_def = self.__find_definition_for_class("main")
        obj = class_def.instantiate_object()
        obj.run_method("main")


program = ['(class main',
           '(method hello_world () (print “hello world!”))',
           ')']

interpreter = Interpreter()
interpreter.run(program)
