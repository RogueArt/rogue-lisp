from __future__ import annotations

from typing import List, Dict, Union, Annotated
from intbase import InterpreterBase, ErrorType

from bparser import BParser
from intbase import InterpreterBase
from v2_constants import *
from v2_method_def import MethodDefinition
from v2_value_def import ValueHelper, Value

BrewinAsPythonValue = Union[None, int, str, bool, 'ObjectDefinition']

import copy
class ObjectDefinition:
    def __init__(self, interpreter: Interpreter, interpreter_base: InterpreterBase, class_name: str, methods: Dict[str, MethodDefinition], fields: Dict[str, BrewinAsPythonValue]):
        self.interpreter: Interpreter = interpreter
        self.interpreter_base: InterpreterBase = interpreter_base
        self.class_name: str = class_name
        self.methods: Dict[str, MethodDefinition]  = methods
        self.fields: Dict[str, BrewinAsPythonValue]= fields
        self.terminated = False

        # Polymorphism / inheritance
        self.ancestor_objs = []

        # Always add the self reference value
        self.fields[InterpreterBase.ME_DEF] = Value(self, self)

        self.parameter_stack: List[Dict[str, BrewinAsPythonValue]] = [{}]
        self.parameters: Dict[str, BrewinAsPythonValue] = self.parameter_stack[-1]

        self.local_variables_stack: List[Dict[str, BrewinAsPythonValue]] = [{}]
        self.local_variables = self.local_variables_stack[-1]

        self.method_stack = []
        self.current_method = None

    # <========== POLYMORPHISM & INHERITANCE ===========>
    def set_ancestor_objs(self, ancestor_objs: List[ObjectDefinition]) -> None:
        self.ancestor_objs = ancestor_objs

    # <========== CODE RUNNERS ============>
    # Interpret the specified method using the provided parameters
    def call_method(self, method_name: str, parameters_map: Dict[str, BrewinAsPythonValue]):
        # Add the parameter list to the call stack
        self.parameter_stack.append(parameters_map)
        self.parameters = self.parameter_stack[-1]
        self.terminated = False

        method = self.get_method_with_name(method_name)
        self.final_result = Value(method.return_type, ValueHelper.get_default_value_for_return_type(method.return_type))

        statement = method.get_top_level_statement()
        self.method_stack.append(method)
        self.current_method = self.method_stack[-1]

        self.__run_statement(statement)

        # Reset the conditions
        # Pop the parameter list from the call stack
        self.parameter_stack.pop()
        self.parameters = self.parameter_stack[-1]

        # We need this because of how the recursion works
        # Imagine if we do call1 -> call2 -> call 3
        # If call3 terminates, we'd still want call2 to keep running
        self.terminated = False

        self.method_stack.pop()
        self.current_method = None if len(self.method_stack) == 0 else self.method_stack[-1]

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
    def is_a_print_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.PRINT_DEF

    def is_a_set_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.SET_DEF

    def is_an_input_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.INPUT_INT_DEF or statement[0] == InterpreterBase.INPUT_STRING_DEF

    def is_a_call_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.CALL_DEF

    def is_a_while_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.WHILE_DEF

    def is_an_if_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.IF_DEF

    def is_a_return_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.RETURN_DEF

    def is_a_begin_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.BEGIN_DEF

    def is_a_let_statement(self, statement: Annotated[list[str], 1]) -> bool:
        return statement[0] == InterpreterBase.LET_DEF

    #  <========== GETTERS AND SETTERS ===========>
    def get_method_with_name(self, method_name: str) -> None|MethodDefinition:
        if method_name in self.methods:
            return self.methods[method_name]
        self.interpreter_base.error(ErrorType.NAME_ERROR)

    def has_method_with_name(self, method_name) -> bool:
        return method_name in self.methods

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

    def get_variable_with_name(self, name: str) -> BrewinAsPythonValue:
        # 1. Check local variables first
        if name in self.local_variables:
            return self.local_variables[name]

        # 2. Check parameter level scope for method
        if name in self.parameters:
            return self.parameters[name]

        # 3. Check field level scope for object
        return self.fields[name] if name in self.fields else self.interpreter_base.error(ErrorType.NAME_ERROR)

    def update_variable_with_name(self, name: str, new_val: BrewinAsPythonValue) -> None:
        # Type check to see if we can update the variable
        variable = self.get_variable_with_name(name)
        if not ValueHelper.is_value_compatible_with_variable(new_val, variable):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        # Check in order of increasing scope
        # 1. Check local variables first
        if name in self.local_variables:
            self.local_variables[name].set_value_to_other(new_val)
            return

        # 2. Check the parameter stack
        if name in self.parameters:
            self.parameters[name].set_value_to_other(new_val)
            return

        # 2. Check the fields of the object
        self.fields[name].set_value_to_other(new_val)

    # <==== EVALUATION & VALUE HANDLER =========>
    def evaluate_expression(self, expression) -> Value:
        # Arrived a singular value, not a list
        # Case 1: Reached a variable
        # Case 2: Reached a const value
        if not isinstance(expression, list):
            # Case 1: Reached a variable
            if self.has_variable_with_name(expression):
                return self.get_variable_with_name(expression)

            # Case 2: Reached a const value
            val = ValueHelper.parse_str_into_python_value(self.interpreter, expression)
            # TO-DO: Update this to handle all types of error types
            return Value(ValueHelper.get_type_from_value(val), val)

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

            return Value(ValueHelper.get_type_from_value(val), val)

        # Case 5: Reached a triple -- we need to recurse and evaluaute this binary expression
        if isinstance(expression, list) and len(expression) == 3:
            operator, operand1, operand2 = expression

            evaluated_expr1 = self.evaluate_expression(operand1)
            evaluated_expr2 = self.evaluate_expression(operand2)
            type1, operand1 = evaluated_expr1.type(), evaluated_expr1.value()
            type2, operand2 = evaluated_expr2.type(), evaluated_expr2.value()

            # Case 5a: Operands must be of the same type
            # Except in the case of a None and Object comparison
            if not ValueHelper.is_value_compatible_with_value(evaluated_expr1, evaluated_expr2):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Case 5b: Operands must be compatible with operator
            if not ValueHelper.is_operand_compatible_with_operator(operator, operand1) or not ValueHelper.is_operand_compatible_with_operator(operator, operand2):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Case 5c: Both are compatible and of the same type, so evaluate them
            match operator:
                case '+':
                    return Value(type1, operand1 + operand2)
                case '-':
                    return Value(int, operand1 - operand2)
                case '*':
                    return Value(int, operand1 * operand2)
                case '/':
                    return Value(int, operand1 // operand2)
                case '%':
                    return Value(int, operand1 % operand2)
                case '==':
                    return Value(bool, operand1 == operand2)
                case '!=':
                    return Value(bool, operand1 != operand2)
                case '>':
                    return Value(bool, operand1 > operand2)
                case '<':
                    return Value(bool, operand1 < operand2)
                case '>=':
                    return Value(bool, operand1 >= operand2)
                case '<=':
                    return Value(bool, operand1 <= operand2)
                case '&':
                    return Value(bool, operand1 and operand2)
                case '|':
                    return Value(bool, operand1 or operand2)

        # Case 6: Reached a pair (one operator, one operand) -- we need to recurse and evaluate this unary expression
        if isinstance(expression, list) and len(expression) == 2:
            operator, operand = expression
            evaluated_expr = self.evaluate_expression(operand)
            operand = evaluated_expr.value()

            if not isinstance(operand, bool):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            if operator == '!':
                return Value(bool, not operand)

        # Case 7: Error - invalid expression format
        raise Exception("Invalid expression format")

    # <========= END EXPRESSION HANDLER ============>
    def __execute_print_statement(self, statement) -> None:

        formatted_arguments = []
        for arg in statement[1:]:
            val = self.evaluate_expression(arg).value()
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
        if not ValueHelper.is_value_compatible_with_variable(val, self.get_variable_with_name(field_name)):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        self.update_variable_with_name(field_name, val)
        return

    def __execute_input_statement(self, statement) -> None:
        input_type, field_name = statement

        # Get and parse the user's input value
        input_val = self.interpreter_base.get_input()
        if input_type == InterpreterBase.INPUT_INT_DEF:
            value = ValueHelper.parse_str_into_python_value(self.interpreter, input_val)
        else:
            value = input_val

        update_value = Value(ValueHelper.get_type_from_value(value), value)

        # Update the variable with the new value
        self.update_variable_with_name(field_name, update_value)
        return

    def __execute_call_statement(self, statement) -> BrewinAsPythonValue:
        obj_name, method_name, param_expressions = statement[1], statement[2], statement[3:]
        
        # Get object based on if it's the current or some other object
        # TO-DO: Refactor this so it's just self.evaluate_expression()
        obj = self if obj_name == InterpreterBase.ME_DEF else self.evaluate_expression(obj_name).value()

        # Call made to object reference of null must generate an error
        if obj is None:
            self.interpreter_base.error(ErrorType.FAULT_ERROR)

        # TO-DO: Move this code block into a function
        # Get the method from object
        method = None
        if obj.has_method_with_name(method_name):
            method = obj.get_method_with_name(method_name)

        # If it doesn't exist, then get it from its ancestors
        # Method call is now being simulated within the ancestor object
        if method is None:
            for ancestor_obj in obj.ancestor_objs:
                if ancestor_obj.has_method_with_name(method_name):
                    method = ancestor_obj.get_method_with_name(method_name)
                    obj = ancestor_obj
                    break 

        # Call made to a method name that does not exist must generate an error
        if method is None:
            self.interpreter_base.error(ErrorType.FAULT_ERROR)

        # Number of parameters does not match the method definition
        if len(param_expressions) != len(method.parameter_names):
            self.interpreter_base.error(ErrorType.NAME_ERROR) # TO-DO: Double check error type

        # Parameters to the method are any variable, constant, or expression
        # We evaluate each expression and create a map of parameter names to values
        parameter_map = {}
        for index, expression in enumerate(param_expressions):
            # Get the value for each variable name
            evaluated_expr = self.evaluate_expression(expression)

            # Update map with the appropriate parameter names
            parameter_name = method.parameter_names[index]
            parameter_type = method.parameter_types[index]

            parameter_variable = Value(parameter_type, None)

            # Type check the value with the parameter type before adding to map
            if not ValueHelper.is_value_compatible_with_variable(evaluated_expr, parameter_variable):
                self.interpreter_base.error(ErrorType.NAME_ERROR) # TO-DO: Double check error type

            # Add to map
            parameter_map[parameter_name] = Value(parameter_type, evaluated_expr.value())

        # TO-DO: Move this code to another region?
        # Account for case in which we call another function with local variable
        self.local_variables_stack.append({})
        self.local_variables = self.local_variables_stack[-1]

        # TO-DO: Add setting parameter values
        # Run the method on the object
        # To-DO: Why am I doing self.result here? Why not just result?
        self.result = obj.call_method(method_name, parameter_map)

        # TO-DO: Move this code to another region?
        self.local_variables_stack.pop()
        self.local_variables = self.local_variables_stack[-1]

        return self.result

    def __execute_while_statement(self, statement) -> None:
        should_execute = self.evaluate_expression(statement[1]).value()

        # Should always evaluate to a boolean condition
        if not isinstance(should_execute, bool):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        if should_execute and not self.terminated:
            self.__run_statement(statement[2])
            self.__execute_while_statement(statement)

        return

    def __execute_if_statement(self, statement) -> BrewinAsPythonValue:
        should_execute = self.evaluate_expression(statement[1]).value()

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
            # return None

        # Any expression evaluated in return statement is the "final" value of method call
        self.final_result = self.evaluate_expression(statement[1])
        default_value = Value(self.current_method.return_type, ValueHelper.get_default_value_for_return_type(self.current_method.return_type))

        # Type check the final result with the return type
        if not ValueHelper.is_value_compatible_with_value(self.final_result, default_value):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        return

    def __execute_all_sub_statements_of_begin_statement(self, statement) -> None:
        for sub_statement in statement[1:]:
            self.__run_statement(sub_statement)

    def __execute_let_statement(self, statement) -> None:
        # Get local parameters added in this scope
        # As we get more and more nested, we should be able to refer to the outer scopes as well
        parsed_local_variables = ValueHelper.parse_let_declarations(self.interpreter, statement[1])
        for variable_name, variable_info in self.local_variables.items():
            # Only add variables that can't be shadowed
            if variable_name not in parsed_local_variables:
                parsed_local_variables[variable_name] = variable_info

        self.local_variables_stack.append(parsed_local_variables)
        self.local_variables = self.local_variables_stack[-1]

        # Behave same as begin statement -- begin executing lines
        for sub_statement in statement[2:]:
            self.__run_statement(sub_statement)

        # Make sure to pop local variables once done executing
        self.local_variables_stack.pop()
        self.local_variables = self.local_variables_stack[-1]

