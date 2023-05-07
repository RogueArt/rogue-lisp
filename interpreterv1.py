from typing import List, Dict
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint
import copy

# Testing only
from testing import get_test_programs, fn
debug = 0


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
    def __init__(self, interpreter, interpreter_base: InterpreterBase, methods: Dict[str, MethodDefinition], fields: Dict[str, any]):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.methods = methods
        self.fields = fields
        self.result = None

    # <========== CODE RUNNERS ============>
    # Interpret the specified method using the provided parameters
    def call_method(self, method_name: str, parameters: List[str]):
        method = self.get_method_with_name(method_name)
        statement = method.get_top_level_statement()
        result = self.__run_statement(statement)
        return result

    # runs/interprets the passed-in statement until completion and
    # gets the result, if any
    def __run_statement(self, statement: List[any], parameters: List[str]):
        # TO-DO: Make this into a private variable
        print(statement)

        if self.is_a_print_statement(statement):
            self.result = self.__execute_print_statement(statement)
        elif self.is_a_set_statement(statement):
            self.result = self.__execute_set_statement(statement)
        elif self.is_an_input_statement(statement):
            self.result = self.__execute_input_statement(statement)
        elif self.is_a_call_statement(statement):
            self.result = self.__execute_call_statement(statement)
        elif self.is_a_while_statement(statement):
            self.result = self.__execute_while_statement(statement)
        elif self.is_an_if_statement(statement):
            self.result = self.__execute_if_statement(statement)
        elif self.is_a_return_statement(statement):
            self.result = self.__execute_return_statement(statement)
        elif self.is_a_begin_statement(statement):
            self.result = self.__execute_all_sub_statements_of_begin_statement(
                statement)
        return self.result

    # <========== MATCH STATEMENT ============>
    def is_a_print_statement(self, statement):
        return statement[0] == InterpreterBase.PRINT_DEF

    def is_a_set_statement(self, statement):
        return statement[0] == InterpreterBase.SET_DEF

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
        return statement[0] == InterpreterBase.BEGIN_DEF

    #  <========== GETTERS AND SETTERS ===========>
    def get_method_with_name(self, method_name: str) -> MethodDefinition:
        return self.methods[method_name]

    # Account for scoping
    # Note: we have to explicitly check for this as Python only has "None", not "undefined"
    def has_variable_with_name(self, name: str) -> bool:
        # 1. Check parameter level scope for method
        if name in self.parameters:
            return True

        # 2. Check field level scope for object
        return name in self.fields

    def get_variable_with_name(self, name: str) -> None | int | str | bool:
        # TO-DO: Fix this for method definition
        # 1. Check parameter level scope for method
        if name in self.parameters:
            return self.parameters[name]

        # 2. Check field level scope for object
        return self.fields[name] if name in self.fields else None

    def update_variable_with_name(self, name: str, new_val: None | int | str | bool) -> None:
        # Check in order of increasing scope
        # 1. Check the parameter stack

        # 2. Check the fields of the object
        self.fields[name] = new_val

    # <==== EVALUATION & VALUE HANDLER =========>
    # TO-DO: Have ObjectDefinition inherit this
    def __parse_str_into_python_value(self, value: str) -> None | int | bool | str:
        if value == InterpreterBase.TRUE_DEF:
            return True
        elif value == InterpreterBase.FALSE_DEF:
            return False
        elif value == InterpreterBase.NULL_DEF:
            return None
        elif isinstance(value, str) and value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        elif self.__is_integer_in_string_form(value):
            return int(value)
        elif self.is_variable_name():
            return self.get_variable_with_name(value)
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))

    # For display formatting - convert python value to string
    def __convert_python_value_to_str(self, value) -> str:
        if value is True:
            return InterpreterBase.TRUE_DEF
        elif value is False:
            return InterpreterBase.FALSE_DEF
        elif value is None:
            return InterpreterBase.NULL_DEF
        elif isinstance(value, str):
            return '"' + value + '"'
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))

    # TO-DO: Figure out why this is getting an int
    def __is_integer_in_string_form(self, s: str | int):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    def evaluate_expression(self, expression):
        # Arrived a singular value, not a list
        # Case 1: Reached a const value
        # Case 2: Reached a variable
        if not isinstance(expression, list):
            # TO-DO: Figure out why this is getting a listw
            # Received an integer value
            if isinstance(expression, int):
                return expression
            # Received a string value
            else:
                return self.__parse_str_into_python_value(expression)

        # Case 3: Reached a triple -- we need to recurse and evaluaute this binary expression
        if isinstance(expression, list) and len(expression) == 3:
            operator, operand1, operand2 = expression
            operand1 = self.__parse_str_into_python_value(operand1)
            operand2 = self.__parse_str_into_python_value(operand2)
            # TO-DO: Handle variable names for operands

            # TO-DO: Store the evaluate express code here to improve code reuse
            match operator:
                case '+':
                    return self.evaluate_expression(operand1) + self.evaluate_expression(operand2)
                case '-':
                    return self.evaluate_expression(operand1) - self.evaluate_expression(operand2)
                case '*':
                    return self.evaluate_expression(operand1) * self.evaluate_expression(operand2)
                case '/':
                    return self.evaluate_expression(operand1) // self.evaluate_expression(operand2)
                case '%':
                    return self.evaluate_expression(operand1) % self.evaluate_expression(operand2)
                case '==':
                    return self.evaluate_expression(operand1) == self.evaluate_expression(operand2)
                case '!=':
                    return self.evaluate_expression(operand1) != self.evaluate_expression(operand2)
                case '>':
                    return self.evaluate_expression(operand1) > self.evaluate_expression(operand2)
                case '<':
                    return self.evaluate_expression(operand1) < self.evaluate_expression(operand2)
                case '>=':
                    return self.evaluate_expression(operand1) >= self.evaluate_expression(operand2)
                case '<=':
                    return self.evaluate_expression(operand1) <= self.evaluate_expression(operand2)
                case '&':
                    return self.evaluate_expression(operand1) and self.evaluate_expression(operand2)
                case '|':
                    return self.evaluate_expression(operand1) or self.evaluate_expression(operand2)

        # Case 4: Reached a pair (one operator, one operand) -- we need to recurse and evaluate this unary expression
        if isinstance(expression, list) and len(expression) == 2:
            operator, operand = expression

            operand = self.__parse_str_into_python_value(operand)
            if operator == '!':
                return not self.evaluate_expression(operand)

        # Case 5: Error - invalid expression format
        raise Exception("Invalid expression format")

    # <========= END EXPRESSION HANDLER ============>
    def __execute_print_statement(self, statement):
        # Two cases to handle:
        # 1. Value - we can format and print this directly
        # 2. Variable - we must do a lookup for the variable name
        # 3. Expression - we must do a calculation for this value

        # TO-DO: Refactor
        # TO-DO: Handle function calls
        formatted_arguments = []
        for arg in statement[1:]:
            if isinstance(arg, list):
                formatted_arguments.append(str(self.evaluate_expression(arg)))
            elif isinstance(arg, str) and arg.startswith('"') and arg.endswith('"'):
                formatted_arguments.append(arg[1:-1])
            elif isinstance(arg, str) and arg.lower() in ['true', 'false', 'null'] or arg.isnumeric():
                formatted_arguments.append(str(arg))
            else:
                variable_name = arg
                value = self.get_variable_with_name(variable_name)
                formatted_value = self.__convert_python_value_to_str(value)
                formatted_arguments.append(formatted_value)

        self.interpreter_base.output(' '.join(formatted_arguments))
        return

    def __execute_set_statement(self, statement):
        # Get the simplified result of the expression:
        field_name, expression = statement[1], statement[2]

        # Handle case in which we need to instantiate a new object
        if isinstance(expression, list) and len(expression) == 2 and expression[0] == 'new':
            # Get the class and instantiate a new object of this class
            class_def = self.interpreter.find_definition_for_class(
                expression[1])
            val = class_def.instantiate_object()
        # Otherwise, treat everything as expressions
        else:
            val = self.evaluate_expression(expression)
        self.update_variable_with_name(field_name, val)
        return

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
        for sub_statement in statement[1:]:
            self.__run_statement(sub_statement)
        pass


class ClassDefinition:
    # constructor for a ClassDefinition
    def __init__(self, interpreter, interpreter_base: InterpreterBase, name, methods, fields):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.name = name
        self.methods = methods
        self.fields = fields

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, copy.deepcopy(
            self.methods), copy.deepcopy(self.fields))

        # To-DO: Evaluate if this is a better approach below
        # for method_name, method_def in self.methods.items():
        #     obj.add_method(method_name, method_def)
        # for field_name, field_value in self.fields.items():
        #     obj.add_field(field_name, field_value)
        return obj


class Interpreter(InterpreterBase):
    def __init__(self, console_ouptput=True, trace_output=False):
        # call InterpreterBase's constructor
        super().__init__(console_ouptput, trace_output)

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
        class_def = self.find_definition_for_class("main")
        obj = class_def.instantiate_object()
        obj.call_method("main", [])
        # print(3)

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

    def find_definition_for_class(self, class_name: str):
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

    test_programs = get_test_programs()
    skip_tests = ['simple', 'many_fields', 'set_fields']  # , 'set_fields'
    for count, (program_name, program) in enumerate(test_programs.items()):
        if program_name in skip_tests:
            print(f"Skipping test #{count+1} {program_name}")
            continue

        print(f"Running test #{count+1} {program_name}:")
        interpreter = Interpreter()
        interpreter.run(program)
        print(f"Finished testing {program_name}\n\n")
