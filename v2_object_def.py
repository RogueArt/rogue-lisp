from __future__ import annotations

from typing import List, Dict, Union, Annotated, Tuple
from intbase import InterpreterBase, ErrorType

from bparser import BParser
from intbase import InterpreterBase
from v2_constants import *
from v2_method_def import MethodDefinition
from v2_value_def import ValueHelper, Value, Variable

BrewinAsPythonValue = Union[None, int, str, bool, 'ObjectDefinition']

import copy
class ObjectDefinition:
    def __init__(self, interpreter: Interpreter, interpreter_base: InterpreterBase, class_name: str, class_def: 'ClassDefinition', base_obj, methods: Dict[str, MethodDefinition], fields: Dict[str, BrewinAsPythonValue]):
        self.interpreter: Interpreter = interpreter
        self.interpreter_base: InterpreterBase = interpreter_base
        self.class_name: str = class_name
        self.class_def: 'ClassDefinition' = class_def
        self.methods: Dict[str, MethodDefinition]  = methods
        self.fields: Dict[str, BrewinAsPythonValue]= fields
        self.terminated = False

        # Polymorphism / inheritance
        self.ancestor_objs: List[ObjectDefinition] = []

        # Always add the self reference value
        # For derived classes, we refer to the base object for execution
        base_obj = self if base_obj is None else base_obj
        self.fields[InterpreterBase.ME_DEF] = Variable(base_obj.interpreter, base_obj.class_name, 'null')
        self.fields[InterpreterBase.ME_DEF].value().set_value_to_other_checked(interpreter, Value(base_obj.interpreter, base_obj.class_def, base_obj))

        self.parameter_stack: List[Dict[str, BrewinAsPythonValue]] = [{}]
        self.parameters: Dict[str, BrewinAsPythonValue] = self.parameter_stack[-1]

        self.local_variables_stack: List[Dict[str, BrewinAsPythonValue]] = [{}]
        self.local_variables = self.local_variables_stack[-1]

        self.method_stack = []
        self.current_method = None

    # <========== POLYMORPHISM & INHERITANCE ===========>
    def set_ancestor_objs(self, ancestor_objs: List[ObjectDefinition]) -> None:
        self.ancestor_objs = ancestor_objs

    def append_ancestor_objs(self, ancestor_objs: List[ObjectDefinition]) -> None:
        self.ancestor_objs += ancestor_objs

    # <========== CODE RUNNERS ============>
    # Interpret the specified method using the provided parameters
    def call_method(self, method_name: str, parameters_map: Dict[str, BrewinAsPythonValue]):
        # Add the parameter list to the call stack
        self.parameter_stack.append(parameters_map)
        self.parameters = self.parameter_stack[-1]
        self.terminated = False
        self.final_result = None

        method = self.get_method_with_name(method_name)
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

        # If it's a non-void function and the final result is None, THEN we set a default value
        if self.final_result is None and self.current_method.return_type is not None:
            self.final_result = Value(self.interpreter, self.current_method.return_type, self.current_method.get_default_value_by_return_type())
        # If it's a void function, return a (None, None)
        elif self.current_method.return_type is None:
            self.final_result = Value(self.interpreter, None, None)

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

    def get_variable_with_name(self, name: str) -> Variable:
        # 1. Check local variables first
        if name in self.local_variables:
            return self.local_variables[name]

        # 2. Check parameter level scope for method
        if name in self.parameters:
            return self.parameters[name]

        # 3. Check field level scope for object
        return self.fields[name] if name in self.fields else self.interpreter_base.error(ErrorType.NAME_ERROR)

    def get_value_with_variable_name(self, name: str) -> BrewinAsPythonValue:
        # 1. Check local variables first
        if name in self.local_variables:
            return self.local_variables[name].value()

        # 2. Check parameter level scope for method
        if name in self.parameters:
            return self.parameters[name].value()

        # 3. Check field level scope for object
        return self.fields[name].value() if name in self.fields else self.interpreter_base.error(ErrorType.NAME_ERROR)

    def update_variable_with_name(self, name: str, new_val: Value) -> None:
        # Check in order of increasing scope
        # 1. Check local variables first
        if name in self.local_variables:
            self.local_variables[name].value().set_value_to_other_checked(self.interpreter, new_val)
            return

        # 2. Check the parameter stack
        if name in self.parameters:
            self.parameters[name].value().set_value_to_other_checked(self.interpreter, new_val)
            return

        # 3. Check the fields of the object
        self.fields[name].value().set_value_to_other_checked(self.interpreter, new_val)

    # <==== EVALUATION & VALUE HANDLER =========>
    def evaluate_expression(self, expression) -> Value:
        # Arrived a singular value, not a list
        # Case 1: Reached a variable
        # Case 2: Reached a const value
        if not isinstance(expression, list):
            # Case 1: Reached a variable
            if self.has_variable_with_name(expression):
                return self.get_value_with_variable_name(expression)

            # Case 2: Reached a const value
            value = ValueHelper.parse_str_into_python_value(self.interpreter, expression)
            value_type = ValueHelper.get_type_from_value(value)
            return Value(self.interpreter, value_type, value)

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

            return Value(self.interpreter, ValueHelper.get_type_from_value(val), val)

        # Case 5: Reached a triple -- we need to recurse and evaluaute this binary expression
        if isinstance(expression, list) and len(expression) == 3:
            operator, operand1, operand2 = expression

            program_value1 = self.evaluate_expression(operand1)
            program_value2 = self.evaluate_expression(operand2)
            type1, operand1 = program_value1.type(), program_value1.value()
            type2, operand2 = program_value2.type(), program_value2.value()

            # Case 5a: Operands must be of the same type
            # Except in the case of a None and Object comparison
            if not program_value1.is_compatible_with_other_value(program_value2) and not program_value2.is_compatible_with_other_value(program_value1):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Case 5b: Operands must be compatible with operator
            if not ValueHelper.is_operand_compatible_with_operator(operator, operand1) or not ValueHelper.is_operand_compatible_with_operator(operator, operand2):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Case 5c: Both are compatible and of the same type, so evaluate them
            match operator:
                case '+':
                    return Value(self.interpreter, type1, operand1 + operand2)
                case '-':
                    return Value(self.interpreter, int, operand1 - operand2)
                case '*':
                    return Value(self.interpreter, int, operand1 * operand2)
                case '/':
                    return Value(self.interpreter, int, operand1 // operand2)
                case '%':
                    return Value(self.interpreter, int, operand1 % operand2)
                case '==':
                    return Value(self.interpreter, bool, operand1 == operand2)
                case '!=':
                    return Value(self.interpreter, bool, operand1 != operand2)
                case '>':
                    return Value(self.interpreter, bool, operand1 > operand2)
                case '<':
                    return Value(self.interpreter, bool, operand1 < operand2)
                case '>=':
                    return Value(self.interpreter, bool, operand1 >= operand2)
                case '<=':
                    return Value(self.interpreter, bool, operand1 <= operand2)
                case '&':
                    return Value(self.interpreter, bool, operand1 and operand2)
                case '|':
                    return Value(self.interpreter, bool, operand1 or operand2)

        # Case 6: Reached a pair (one operator, one operand) -- we need to recurse and evaluate this unary expression
        if isinstance(expression, list) and len(expression) == 2:
            operator, operand = expression
            evaluated_expr = self.evaluate_expression(operand)
            operand = evaluated_expr.value()

            if not isinstance(operand, bool):
                self.interpreter_base.error(ErrorType.TYPE_ERROR)

            if operator == '!':
                return Value(self.interpreter, bool, not operand)

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
        program_value = self.evaluate_expression(expression)
        self.update_variable_with_name(field_name, program_value)
        return

    def __execute_input_statement(self, statement) -> None:
        input_type, field_name = statement

        # Get and parse the user's input value
        input_val = self.interpreter_base.get_input()
        if input_type == InterpreterBase.INPUT_INT_DEF:
            value = ValueHelper.parse_str_into_python_value(self.interpreter, input_val)
        else:
            value = input_val

        update_value = Value(self.interpreter, ValueHelper.get_type_from_value(value), value)

        # Update the variable with the new value
        self.update_variable_with_name(field_name, update_value)
        return
    
    def has_method_with_name_and_args(self, obj: ObjectDefinition, method_name: str, parameter_types: List[type]):
        if obj.has_method_with_name(method_name):
            method = obj.get_method_with_name(method_name)
            # Length of parameter types must match
            if len(method.parameter_types) != len(parameter_types):
                return False

            # Pair up the elements and compare
            for method_type, param_type in zip(method.parameter_types, parameter_types):
                if method_type != param_type:
                    continue

            # If length and types match, then we found our method & object
            return True
        return False

    def get_parameter_types_from_expression(self, param_expressions: List[str]) -> List[type]:
        parameter_types = list(map(lambda expr: self.evaluate_expression(expr).type(), param_expressions))
        return parameter_types

    # TO-DO: Maybe rename this to something better?
    # TO-DO: Make this into a dictionary so it doesn't rely on ordering?
    def get_closest_matching_method_and_obj(self, starting_obj: ObjectDefinition, obj_name: str, method_name: str, param_expressions: List[type]) -> Tuple[ObjectDefinition|None, MethodDefinition|None]:
        # Search for a matching method given number of arguments and types
        parameter_types = self.get_parameter_types_from_expression(param_expressions)
        current_obj_and_ancestor_objs = [starting_obj] + starting_obj.ancestor_objs

        # Gather all of the method candidates
        candidates = []
        for candidate_obj in current_obj_and_ancestor_objs:
            if candidate_obj.has_method_with_name_and_args(candidate_obj, method_name, parameter_types):
                candidate_method = candidate_obj.get_method_with_name(method_name) 
                candidates.append((candidate_obj, candidate_method))

        # If the object name was "super", pick the first one whose candidate object is not the current object.
        if obj_name == InterpreterBase.SUPER_DEF:
            for candidate_obj, candidate_method in candidates:
                if candidate_obj != starting_obj:
                    return (candidate_obj, candidate_method)

        # Otherwise, pick the first candidate in this list
        if candidates:
            return candidates[0]
        
        # No matching methods or objects
        return (None, None)


    def __execute_call_statement(self, statement) -> BrewinAsPythonValue:
        obj_name, method_name, param_expressions = statement[1], statement[2], statement[3:]
        
        # Get object based on if it's the current or some other object
        # TO-DO: Refactor this so it's just self.evaluate_expression()
        obj = self if obj_name == InterpreterBase.SUPER_DEF else self.evaluate_expression(obj_name).value()

        # Call made to object reference of null must generate an error
        if obj is None:
            self.interpreter_base.error(ErrorType.FAULT_ERROR) 

        obj, method = self.get_closest_matching_method_and_obj(obj, obj_name, method_name, param_expressions)

        # TO-DO: Refactor this into a method
        # Call made to a method name that does not exist must generate an error
        if method is None:
            self.interpreter_base.error(ErrorType.NAME_ERROR)

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

            # We use this for type checking purposes only
            # Perform type checking before setting
            try:
                parameter_pseudo_variable = Value(self.interpreter, parameter_type, evaluated_expr.value())
            except:
                self.interpreter_base.error(ErrorType.NAME_ERROR)

            # Add variable to map
            parameter_variable = Variable(self.interpreter, '', '', type_override=parameter_type, program_value_override=parameter_pseudo_variable)
            parameter_map[parameter_name] = parameter_variable

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

        # Type check the final result with the return type
        if not self.current_method.check_return_type_compatibility(self.final_result):
            self.interpreter_base.error(ErrorType.TYPE_ERROR)

        # Update the result to match the function type 
        self.final_result.set_type(self.current_method.return_type)

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

