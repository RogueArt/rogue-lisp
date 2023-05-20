from typing import List, Dict
from intbase import InterpreterBase, ErrorType

from v2_method_def import *

class ObjectDefinition:
    def __init__(self, interpreter, interpreter_base: InterpreterBase, methods: Dict[str, MethodDefinition], fields: Dict[str, None|int|bool|str]):
        self.interpreter = interpreter
        self.interpreter_base = interpreter_base
        self.methods = methods
        self.fields = fields
        self.terminated = False
        self.final_result = None

        self.parameter_stack: List[Dict[str, None|int|bool|str]] = [{}]
        self.parameters: Dict[str, None|int|bool|str] = self.parameter_stack[-1]

    # <========== CODE RUNNERS ============>
    # Interpret the specified method using the provided parameters
    def call_method(self, method_name: str, parameters_map: Dict[str, None|int|bool|str]):
        # Add the parameter list to the call stack
        self.parameter_stack.append(parameters_map)
        self.parameters = self.parameter_stack[-1]
        self.terminated = False
        self.final_result = None

        method = self.get_method_with_name(method_name)
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
            self.__execute_all_sub_statements_of_begin_statement(
                statement)
        
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
    def evaluate_expression(self, expression) -> None|int|bool|str:
        # Arrived a singular value, not a list
        # Case 1: Reached a variable
        # Case 2: Reached a const value
        if not isinstance(expression, list):
            # Case 1: Reached a variable
            if self.has_variable_with_name(expression):
                return self.get_variable_with_name(expression)
            
            # Case 2: Reached a const value
            return ValueHelper.parse_str_into_python_value(expression)

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

        # Evaluate expressions befoer setting value
        val = self.evaluate_expression(expression)
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
            value = self.evaluate_expression(expression)

            # Update map with the appropriate parameter names
            parameter_name = method.parameter_names[index]
            parameter_map[parameter_name] = value

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

        return
    
    def __execute_return_statement(self, statement) -> None:
        # Get the final return value
        if len(statement) == 1:
            self.final_result = None
            return None
        
        # Any expression evaluated in return statement is the "final" value of method call
        self.final_result = self.evaluate_expression(statement[1])
        return 

    def __execute_all_sub_statements_of_begin_statement(self, statement) -> None:
        for sub_statement in statement[1:]:
            self.__run_statement(sub_statement)

# TO-DO: Fix the circular import requiring this to be at the bottom
from v2_value_def import *
