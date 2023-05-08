from typing import List, Dict, Union
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint
import copy

NestedList = Union[str, List['NestedList']]

# For debug levels
debug = 0
class MethodDefinition:
    def __init__(self, method_name: str, top_level_statement: list, parameter_names: List[str]):
        self.method_name = method_name
        self.top_level_statement = top_level_statement
        self.parameter_names = parameter_names

    # Top-level statement list in the form of nested lists
    def get_top_level_statement(self):
        return self.top_level_statement

class ObjectDefinition:
    def __init__(self, interpreter, interpreter_base: InterpreterBase, methods: Dict[str, MethodDefinition], fields: Dict[str, None|int|bool|str]):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.methods = methods
        self.fields = fields
        self.terminated = False
        self.final_result = None

        self.parameter_stack: List[Dict[str, None|int|bool|str]] = []
        self.parameters: Dict[str, None|int|bool|str] = {}

    # <========== CODE RUNNERS ============>
    # Interpret the specified method using the provided parameters
    def call_method(self, method_name: str, parameters_map: Dict[str, None|int|bool|str]):
        # Add the parameter list to the call stack
        self.parameter_stack.append(parameters_map)
        self.parameters = self.parameter_stack[-1]
        self.terminated = False

        method = self.get_method_with_name(method_name)
        statement = method.get_top_level_statement()
        result = self.__run_statement(statement)

        # Reset the conditions
        # Pop the parameter list from the call stack
        self.parameter_stack.pop()
        self.parameters = self.parameter_stack[-1] if len(self.parameter_stack) > 0 else {}
        self.terminated = False
        
        saved_result = self.final_result
        self.final_result = None
        return saved_result

    # runs/interprets the passed-in statement until completion and
    # gets the result, if any
    def __run_statement(self, statement: List[any]):
        if debug >= 1:
            print(statement)

        if self.terminated:
            return self.result
        
        # TO-DO: This does literally nothing for the final result
        # Clean this up
        self.result = None
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
            self.terminated = True
        elif self.is_a_begin_statement(statement):
            self.result = self.__execute_all_sub_statements_of_begin_statement(
                statement)
        
        # Default return is None if no other statements updated it
        return self.result

    # <========== MATCH STATEMENT ============>
    def is_a_print_statement(self, statement):
        return statement[0] == InterpreterBase.PRINT_DEF

    def is_a_set_statement(self, statement):
        return statement[0] == InterpreterBase.SET_DEF

    def is_an_input_statement(self, statement):
        return statement[0] == InterpreterBase.INPUT_INT_DEF or statement[0] == InterpreterBase.INPUT_STRING_DEF

    def is_a_call_statement(self, statement):
        return statement[0] == InterpreterBase.CALL_DEF

    def is_a_while_statement(self, statement):
        return statement[0] == InterpreterBase.WHILE_DEF

    def is_an_if_statement(self, statement):
        return statement[0] == InterpreterBase.IF_DEF

    def is_a_return_statement(self, statement):
        return statement[0] == InterpreterBase.RETURN_DEF

    def is_a_begin_statement(self, statement):
        return statement[0] == InterpreterBase.BEGIN_DEF

    #  <========== GETTERS AND SETTERS ===========>
    def get_method_with_name(self, method_name: str) -> MethodDefinition:
        if method_name in self.methods:
            return self.methods[method_name]
        else:
            self.interpreter_base.error(ErrorType.NAME_ERROR)

    # Account for scoping
    # Note: we have to explicitly check for this as Python only has "None", not "undefined"
    def has_variable_with_name(self, name: str) -> bool:
        # 1. Check parameter level scope for method
        if name in self.parameters:
            return True

        # 2. Check field level scope for object
        return name in self.fields

    def get_variable_with_name(self, name: str) -> None | int | str | bool:
        # 1. Check parameter level scope for method
        if name in self.parameters:
            return self.parameters[name]

        # 2. Check field level scope for object
        return self.fields[name] if name in self.fields else self.interpreter_base.error(ErrorType.NAME_ERROR)

    def update_variable_with_name(self, name: str, new_val: None | int | str | bool) -> None:
        # Check in order of increasing scope
        # 1. Check the parameter stack
        if name in self.parameters:
            self.parameters[name] = new_val

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
        elif self.has_variable_with_name(value):
            return self.get_variable_with_name(value)
        else:
            self.interpreter_base.error(ErrorType.NAME_ERROR)

    # For display formatting - convert python value to string
    def __convert_python_value_to_str(self, value) -> str:
        if value is True:
            return InterpreterBase.TRUE_DEF
        elif value is False:
            return InterpreterBase.FALSE_DEF
        elif value is None:
            return InterpreterBase.NULL_DEF
        elif isinstance(value, str):
            return value # '"' + value + '"'
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))

    def __is_integer_in_string_form(self, s: str | int):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    def evaluate_expression(self, expression) -> None|int|bool|str:
        # Arrived a singular value, not a list
        # Case 1: Reached a const value
        # Case 2: Reached a variable
        if not isinstance(expression, list):
            return self.__parse_str_into_python_value(expression)

        # Case 3: Reached a call statement
        if isinstance(expression, list) and expression[0] == InterpreterBase.CALL_DEF:
            val = self.__run_statement(expression)
            return val
        
        # Case 4: Reached a new statement
        if isinstance(expression, list) and expression[0] == InterpreterBase.NEW_DEF:
            # Get the name of the field
            field_name = expression[1]

            # Get the class and instantiate a new object of this class
            class_def = self.interpreter.find_definition_for_class(field_name)
            val = class_def.instantiate_object()

            return val
                
        # Case 5: Reached a triple -- we need to recurse and evaluaute this binary expression       
        if isinstance(expression, list) and len(expression) == 3:
            operator, operand1, operand2 = expression

            operand1 = self.evaluate_expression(operand1)
            operand2 = self.evaluate_expression(operand2)

            # Case 5a: Operands must be of the same type
            # Except in the case of a None and Object comparison
            if (type(operand1) != type(operand2)) and (operand1 is not None and operand2 is not None):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)
            
            # Case 5b: Operands must be compatible with operator
            if not self.is_operand_compatible_with_operator(operator, operand1) or not self.is_operand_compatible_with_operator(operator, operand2):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Case 5c: Both are compatible and of same type, so evaluate them
            match operator:
                case '+':
                    return operand1 + operand2
                case '-':
                    return operand1 - operand2
                case '*':
                    return operand1 * operand2
                case '/':
                    return operand1 // operand2
                case '%':
                    return operand1 % operand2
                case '==':
                    return operand1 == operand2
                case '!=':
                    return operand1 != operand2
                case '>':
                    return operand1 > operand2
                case '<':
                    return operand1 < operand2
                case '>=':
                    return operand1 >= operand2
                case '<=':
                    return operand1 <= operand2
                case '&':
                    return operand1 and operand2
                case '|':
                    return operand1 or operand2

        # Case 6: Reached a pair (one operator, one operand) -- we need to recurse and evaluate this unary expression
        if isinstance(expression, list) and len(expression) == 2:
            operator, operand = expression
            operand = self.evaluate_expression(operand)

            if not isinstance(operand, bool):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            if operator == '!':
                return not operand

        # Case 7: Error - invalid expression format
        raise Exception("Invalid expression format")

    # <========= END EXPRESSION HANDLER ============>
    def is_operand_compatible_with_operator(self, operator: str, operand) -> bool:
        if isinstance(operand, str) and operator == '+':
            return True  # String concatenation is allowed with the + operator
        elif isinstance(operand, int) and operator in ['+', '-', '*', '/', '%']:
            return True  # Integer arithmetic is allowed with the +, -, *, /, and % operators
        elif isinstance(operand, int) and operator in ['<', '>', '<=', '>=', '!=', '==']:
            return True  # Integer comparison is allowed with the <, >, <=, >=, !=, and == operators
        elif isinstance(operand, str) and operator in ['<', '>', '<=', '>=', '!=', '==']:
            return True  # String comparison is allowed with the <, >, <=, >=, !=, and == operators
        elif isinstance(operand, bool) and operator in ['&', '|', '==', '!=']:
            return True  # Boolean comparison is allowed with the & (AND), | (OR), ==, and != operators
        elif operand is None and operator in ['==', '!=']:
            return True  # Null comparison is allowed with the == and != operators
        elif isinstance(operand, ObjectDefinition) and operator in ['==', '!=']:
            return True # Object comparison is allowed with the == and != operators 
        elif operator == '!':
            return isinstance(operand, bool)  # Unary NOT is only allowed with booleans
        else:
            return False  # Operand and operator are not compatible

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
                val = self.evaluate_expression(arg)
                formatted_val = self.__convert_python_value_to_str(val)
                formatted_arguments.append(formatted_val)
            elif isinstance(arg, str) and arg.startswith('"') and arg.endswith('"'):
                formatted_arguments.append(arg[1:-1])
            elif isinstance(arg, str) and arg.lower() in [InterpreterBase.TRUE_DEF, InterpreterBase.FALSE_DEF, InterpreterBase.NULL_DEF] or arg.isnumeric():
                formatted_arguments.append(str(arg))
            else:
                variable_name = arg
                value = self.get_variable_with_name(variable_name)
                formatted_value = self.__convert_python_value_to_str(value)
                formatted_arguments.append(formatted_value)

        if debug >= 1:
            print(formatted_arguments)
        self.interpreter_base.output(''.join(formatted_arguments))
        return

    def __execute_set_statement(self, statement) -> None:
        # Get the simplified result of the expression:
        field_name, expression = statement[1], statement[2]

        # Throw error if the variable we're setting does not exist
        if not self.has_variable_with_name(field_name):
            self.interpreter_base.error(ErrorType.NAME_ERROR)

        # Handle case in which we need to instantiate a new object
        # Otherwise, treat everything as expressions
        # else:
        val = self.evaluate_expression(expression)
        self.update_variable_with_name(field_name, val)
        return

    def __execute_input_statement(self, statement) -> None:
        input_type, field_name = statement

        # Get and parse the user's input value
        input_val = self.interpreter_base.get_input()
        if input_type == InterpreterBase.INPUT_INT_DEF:
            value = self.__parse_str_into_python_value(input_val)
        else:
            value = input_val

        # Update the variable with the new value
        self.update_variable_with_name(field_name, value)
        return

    def __execute_call_statement(self, statement) -> None|int|str|bool:
        obj_name, method_name, param_expressions = statement[1], statement[2], statement[3:]

        # Get object based on if it's the current or some other object
        obj = self if obj_name == InterpreterBase.ME_DEF else self.evaluate_expression(obj_name)

        # Call made to object reference of null must generate an error
        if obj is None:
            self.interpreter_base.error(ErrorType.FAULT_ERROR)

        # Parameters to the method are any variable, constant, or expression
        # We evaluate each expression and create a map of parameter names to values
        parameter_map = {}
        method = obj.get_method_with_name(method_name)

        # Call made to a method name that does not exist must generate an error
        if method is None:
            self.interpreter_base.error(ErrorType.FAULT_ERROR)

        # Number of parameters does not match the method definition
        if len(param_expressions) != len(method.parameter_names):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        for index, expression in enumerate(param_expressions):
            # Get the value for each variable name
            value = obj.evaluate_expression(expression)

            # Update map with the appropriate parameter names
            parameter_name = method.parameter_names[index]
            parameter_map[parameter_name] = value

        # TO-DO: Add setting parameter values
        # Run the method on the object
        # To-DO: Why am I doing self.result here? Why not just result?
        self.result = obj.call_method(method_name, parameter_map)
        return self.result

    def __execute_while_statement(self, statement) -> None|int|str|bool:
        result = None

        should_execute = self.evaluate_expression(statement[1])

        # Should always evaluate to a boolean condition
        if not isinstance(should_execute, bool):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        if should_execute and not self.terminated:
            self.__run_statement(statement[2])
            self.__execute_while_statement(statement)
        
        return result

    def __execute_if_statement(self, statement) -> None|int|str|bool:        
        should_execute = self.evaluate_expression(statement[1])

        # Should always evaluate to a boolean condition
        if not isinstance(should_execute, bool):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        # Handles variant of if (expr) (statemetnA)
        if should_execute:
            return self.__run_statement(statement[2])
        # Handles variant of if (expr) (statementA) (statementB)
        elif not should_execute and len(statement) == 4:
            return self.__run_statement(statement[3])

        return None
    
    def __execute_return_statement(self, statement) -> None|int|str|bool:
        # Get the final return value
        if len(statement) == 1:
            self.final_result = None
            return None
        
        # We do two things here
        # 1. Any expression evaluated in return statement is the "final" value of method call
        val = self.evaluate_expression(statement[1])
        self.final_result = val

        # 2. Set a terminated flag to block any further execution of sibling statements
        self.terminated = True
        return val

    def __execute_all_sub_statements_of_begin_statement(self, statement):
        for sub_statement in statement[1:]:
            self.__run_statement(sub_statement)

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
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, 
                               copy.deepcopy(self.methods), copy.deepcopy(self.fields))
        return obj

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
        class_def = self.find_definition_for_class("main")
        obj = class_def.instantiate_object()
        obj.call_method("main", {})

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

                value: List[str] = self.__parse_str_into_python_value(
                    statement[2])

                # Fields map stores <name:value> pairs
                fields[field_name] = value

        return fields

    def find_definition_for_class(self, class_name: str):
        # Check if class exists
        if class_name in self.class_definitions:
            return self.class_definitions[class_name]
        
        # If not found, then throw an error for trying to get invalid class
        self.interpreter_base.error(ErrorType.TYPE_ERROR)

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
