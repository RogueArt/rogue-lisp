from typing import List, Dict
from intbase import InterpreterBase, ErrorType

from v2_method_def import *
# from v2_class_def import value
from bparser import BParser
from intbase import InterpreterBase
from v2_object_def import *

import copy


class ObjectDefinition:
    def __init__(self, interpreter, interpreter_base: InterpreterBase, class_name: str, methods: Dict[str, MethodDefinition], fields: Dict[str, None | int | bool | str]):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.class_name = class_name
        self.methods = methods
        self.fields = fields
        self.terminated = False

        self.parameter_stack: List[Dict[str, None | int | bool | str]] = [{}]
        self.parameters: Dict[str, None | int | bool | str] = self.parameter_stack[-1]

        self.local_variables_stack = [{}]
        self.local_variables = self.local_variables_stack[-1]

    # <========== CODE RUNNERS ============>
    # Interpret the specified method using the provided parameters
    def call_method(self, method_name: str, parameters_map: Dict[str, None | int | bool | str]):
        # Add the parameter list to the call stack
        self.parameter_stack.append(parameters_map)
        self.parameters = self.parameter_stack[-1]
        self.terminated = False
        self.final_result = None

        method = self.get_method_with_name(method_name)
        self.final_result = ValueHelper.get_default_value_for_return_type(
            method.return_type)
        statement = method.get_top_level_statement()
        self.__run_statement(statement)

        # Reset the conditions
        # Pop the parameter list from the call stack
        self.parameter_stack.pop()
        self.parameters = self.parameter_stack[-1]

        # We need this because of how the recursion works
        # Imagine if we do call1 -> call2 -> call 3
        # If call3 terminates, we'd still want call2 to keep running
        self.terminated = False
        return self.final_result

    # runs/interprets the passed-in statement until completion and
    # gets the result, if any
    def __run_statement(self, statement: List[any]) -> None:
        if debug >= 1:
            print(statement)

        if self.terminated:
            return

        if self.is_a_print_statement(statement):
            self.__execute_print_statement(statement)
        elif self.is_a_set_statement(statement):
            self.__execute_set_statement(statement)
        elif self.is_an_input_statement(statement):
            self.__execute_input_statement(statement)
        elif self.is_a_call_statement(statement):
            self.__execute_call_statement(statement)
        elif self.is_a_while_statement(statement):
            self.__execute_while_statement(statement)
        elif self.is_an_if_statement(statement):
            self.__execute_if_statement(statement)
        elif self.is_a_return_statement(statement):
            self.__execute_return_statement(statement)
            # Use this to block executing of any sibling methods
            self.terminated = True
        elif self.is_a_begin_statement(statement):
            self.__execute_all_sub_statements_of_begin_statement(statement)
        elif self.is_a_let_statement(statement):
            self.__execute_let_statement(statement)

        return

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

    def is_a_let_statement(self, statement):
        return statement[0] == InterpreterBase.LET_DEF

    #  <========== GETTERS AND SETTERS ===========>
    def get_method_with_name(self, method_name: str) -> MethodDefinition:
        if method_name in self.methods:
            return self.methods[method_name]
        else:
            self.interpreter_base.error(ErrorType.NAME_ERROR)

    # Account for scoping
    # Note: we have to explicitly check for this as Python only has "None", not "undefined"
    def has_variable_with_name(self, name: str) -> bool:
        # 1. Check in local variables first
        if name in self.local_variables:
            return True

        # 2. Check parameter level scope for method
        if name in self.parameters:
            return True

        # 3. Check field level scope for object
        return name in self.fields

    def get_variable_with_name(self, name: str) -> None | int | str | bool:
        # 1. Check local variables first
        if name in self.local_variables:
            return self.local_variables[name]

        # 2. Check parameter level scope for method
        if name in self.parameters:
            return self.parameters[name]

        # 3. Check field level scope for object
        return self.fields[name] if name in self.fields else self.interpreter_base.error(ErrorType.NAME_ERROR)

    def update_variable_with_name(self, name: str, new_val: None | int | str | bool) -> None:
        # Type check to see if we can update the v ariable
        if not ValueHelper.is_value_compatible_with_type(new_val, self.get_variable_with_name(name)['type']):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        # Check in order of increasing scope
        # 1. Check local variables first
        if name in self.local_variables:
            self.parameters[name]['value'] = new_val
            return

        # 2. Check the parameter stack
        if name in self.parameters:
            self.parameters[name]['value'] = new_val
            return

        # 2. Check the fields of the object
        self.fields[name]['value'] = new_val

    # <==== EVALUATION & VALUE HANDLER =========>
    def evaluate_expression(self, expression) -> None | int | bool | str:
        # Arrived a singular value, not a list
        # Case 1: Reached a variable
        # Case 2: Reached a const value
        if not isinstance(expression, list):
            # Case 1: Reached a variable
            if self.has_variable_with_name(expression):
                return self.get_variable_with_name(expression)['value']

            # Case 2: Reached a const value
            val = ValueHelper.parse_str_into_python_value(expression)
            # TO-DO: Update this to handle all types of error types
            if val == ErrorType.NAME_ERROR:
                self.interpreter_base.error(ErrorType.NAME_ERROR)
            return val

        # Case 3: Reached a call statement
        if isinstance(expression, list) and expression[0] == InterpreterBase.CALL_DEF:
            return self.__execute_call_statement(expression)

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
            if not ValueHelper.is_operand_compatible_with_operand(operand1, operand2):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Case 5b: Operands must be compatible with operator
            if not ValueHelper.is_operand_compatible_with_operator(operator, operand1) or not ValueHelper.is_operand_compatible_with_operator(operator, operand2):
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
    def __execute_print_statement(self, statement) -> None:

        formatted_arguments = []
        for arg in statement[1:]:
            val = self.evaluate_expression(arg)
            formatted_val = ValueHelper.convert_python_value_to_str(val)
            formatted_arguments.append(formatted_val)

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

        # Evaluate expressions before setting value
        val = self.evaluate_expression(expression)

        # Throw error if the variable's type doesn't match value
        if not ValueHelper.is_operand_compatible_with_operand(self.get_variable_with_name(field_name), val):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        self.update_variable_with_name(field_name, val)
        return

    def __execute_input_statement(self, statement) -> None:
        input_type, field_name = statement

        # Get and parse the user's input value
        input_val = self.interpreter_base.get_input()
        if input_type == InterpreterBase.INPUT_INT_DEF:
            value = ValueHelper.parse_str_into_python_value(input_val)
        else:
            value = input_val

        # Update the variable with the new value
        self.update_variable_with_name(field_name, value)
        return

    def __execute_call_statement(self, statement) -> None | int | str | bool:
        obj_name, method_name, param_expressions = statement[1], statement[2], statement[3:]

        # Get object based on if it's the current or some other object
        obj = self if obj_name == InterpreterBase.ME_DEF else self.evaluate_expression(
            obj_name)

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
            value = self.evaluate_expression(expression)

            # Update map with the appropriate parameter names
            parameter_name = method.parameter_names[index]
            parameter_type = method.parameter_types[index]

            # Type check the value with the parameter type before adding to map
            if not ValueHelper.is_value_compatible_with_type(value, parameter_type):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Add to map
            parameter_map[parameter_name] = {
                'type': parameter_type, 'value': value}

        # TO-DO: Add setting parameter values
        # Run the method on the object
        # To-DO: Why am I doing self.result here? Why not just result?
        self.result = obj.call_method(method_name, parameter_map)
        return self.result

    def __execute_while_statement(self, statement) -> None:
        should_execute = self.evaluate_expression(statement[1])

        # Should always evaluate to a boolean condition
        if not isinstance(should_execute, bool):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        if should_execute and not self.terminated:
            self.__run_statement(statement[2])
            self.__execute_while_statement(statement)

        return

    def __execute_if_statement(self, statement) -> None | int | str | bool:
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

        return

    def __execute_return_statement(self, statement) -> None:
        # Get the final return value
        if len(statement) == 1:
            return
            # self.final_result = None
            # return None

        # Any expression evaluated in return statement is the "final" value of method call
        self.final_result = self.evaluate_expression(statement[1])
        return

    def __execute_all_sub_statements_of_begin_statement(self, statement) -> None:
        for sub_statement in statement[1:]:
            self.__run_statement(sub_statement)

    def __execute_let_statement(self, statement) -> None:
        # Initialize and add the local variables
        parsed_local_variables = ValueHelper.parse_let_declarations(self.interpreter, statement[1])
        self.local_variables_stack.append(parsed_local_variables)
        self.local_variables = self.local_variables_stack[-1]

        # Behave same as begin statement -- begin executing lines
        for sub_statement in statement[2:]:
            self.__run_statement(sub_statement)

        # Make sure to pop local variables once done executing
        self.local_variables_stack.pop()
        self.local_variables = self.local_variables_stack[-1]


class ValueHelper():
    def parse_str_into_python_value(value: str) -> None | int | bool | str:
        if value == InterpreterBase.TRUE_DEF:
            return True
        elif value == InterpreterBase.FALSE_DEF:
            return False
        elif value == InterpreterBase.NULL_DEF:
            return None
        elif isinstance(value, str) and value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        elif value.lstrip('-').isnumeric():
            return int(value)
        else:
            # TO-DO: Design this class better to not have to return this
            return ErrorType.NAME_ERROR

    # For display formatting - convert python value to string
    def convert_python_value_to_str(value) -> str:
        if value is True:
            return InterpreterBase.TRUE_DEF
        elif value is False:
            return InterpreterBase.FALSE_DEF
        elif value is None or isinstance(value, ObjectDefinition):
            return InterpreterBase.NULL_DEF
        elif isinstance(value, str):
            return value  # '"' + value + '"'
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))

    def is_operand_compatible_with_operator(operator: str, operand) -> bool:
        if isinstance(operand, str) and operator == '+':
            return True  # String concatenation is allowed with the + operator
        elif type(operand) is int and operator in ['+', '-', '*', '/', '%']:
            return True  # Integer arithmetic is allowed with the +, -, *, /, and % operators
        elif isinstance(operand, int) and operator in ['<', '>', '<=', '>=', '!=', '==']:
            return True  # Integer comparison is allowed with the <, >, <=, >=, !=, and == operators
        elif isinstance(operand, str) and operator in ['<', '>', '<=', '>=', '!=', '==']:
            return True  # String comparison is allowed with the <, >, <=, >=, !=, and == operators
        elif isinstance(operand, bool) and operator in ['&', '|', '==', '!=']:
            # Boolean comparison is allowed with the & (AND), | (OR), ==, and != operators
            return True
        elif operand is None and operator in ['==', '!=']:
            return True  # Null comparison is allowed with the == and != operators
        elif isinstance(operand, ObjectDefinition) and operator in ['==', '!=']:
            return True  # Object comparison is allowed with the == and != operators
        elif operator == '!':
            # Unary NOT is only allowed with booleans
            return isinstance(operand, bool)
        else:
            return False  # Operand and operator are not compatible

    def is_operand_compatible_with_operand(operand1, operand2) -> bool:
        # If both operands are primitives, then if types don't match, not compatible
        if ValueHelper.is_primitive_type(operand1) or ValueHelper.is_primitive_type(operand2):
            return type(operand1) == type(operand2)

        # Object definition type - can be None or Class
        return True

    # In Brewin, string, int, and bool are primitive types
    def is_primitive_type(value):
        return isinstance(value, str) or isinstance(value, int) or isinstance(value, bool)

    # Parameters list comes in as [type_str, argument_name], we need to convert this to a list of types
    def parse_expected_types_from_parameters_list(interpreter, params_list: List[List[str]]) -> List[type]:
        return [ValueHelper.get_variable_type_from_type_str(interpreter, param_type) for param_type, _ in params_list]

    def parse_parameter_names_from_parameters_list(params_list: List[List[str]]) -> List[str]:
        return [param[1] for param in params_list]

    # TO-DO: Use a better variable naming scheme
    def parse_let_declarations(interpreter, params_list: List[List[str]]) -> Dict[str, str]:
        local_variables = {}
        for param_triple in params_list:
            # Parse type, value, and name
            return_type: type = ValueHelper.get_variable_type_from_type_str(interpreter, param_triple[0])
            variable_name: str = param_triple[1]
            value = ValueHelper.parse_str_into_python_value(param_triple[2])
            
            # Type check the value with the parameter type before adding to map
            if not ValueHelper.is_value_compatible_with_type(value, return_type):
                interpreter.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Check that the variable hasn't already been added yet
            if variable_name in local_variables:
                interpreter.interpreter_base.error(ErrorType.NAME_ERROR)

            # Add to map
            local_variables[variable_name] = { 'type': return_type, 'value': value }

        return local_variables
    
    # <===================== STATIC TYPE CHECKING ========================>

    def is_value_compatible_with_type(value: int | bool | str | None | ObjectDefinition, parsed_type: type) -> bool:
        # Case 1 - Primitives
        if ValueHelper.is_primitive_type(parsed_type):
            return type(value) == parsed_type

        # Case 2 - Object definition
        # TO-DO: Handle derived objects
        if isinstance(parsed_type, ClassDefinition):
            return value is None or parsed_type.name == value.class_name

        # Case 3
        return False

    # def get_type_from_value(value: int|bool|str|None|ObjectDefinition) -> type:
    #     if ValueHelper.is_primitive_type(type(value)):
    #         return type(value)

    #     if isinstance(value, ObjectDefinition):

    #     pass

    def is_primitive_type(expected_type):
        return expected_type in [int, str, bool]

    def get_variable_type_from_type_str(interpreter, type_str: str):
        if type_str == "int":
            return int
        elif type_str == "string":
            return str
        elif type_str == "bool":
            return bool

        # If not a primitive type, then it must be a class
        return interpreter.find_definition_for_class(type_str)

    def get_return_type_from_type_str(interpreter, type_str):
        if type_str == 'void':
            return None
        else:
            return ValueHelper.get_variable_type_from_type_str(interpreter, type_str)

    def get_default_value_for_return_type(return_type):
        if return_type is int:
            return 0
        elif return_type is str:
            return ''
        elif return_type is bool:
            return False
        # TO-DO: Check the case where nothing is returned vs null object
        else:
            return None


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
        obj = ObjectDefinition(self.interpreter, self.interpreter_base, self.name,
                               copy.deepcopy(self.methods), copy.deepcopy(self.fields))
        return obj
