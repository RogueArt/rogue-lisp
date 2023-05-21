from intbase import InterpreterBase, ErrorType
from v2_constants import *


# TO-DO: Make this implementation more idiomatic
# NOTHING='None'
# NOTHING_TYPE='0c58a8606378b9c71f742fd385c90b99123213'

# VOID_TYPE='0c58a8606378b9c71f742fd385c90b99123213'
SENTINEL_VALUE='0c58a8606378b9c71f742fd385c90b99123213'
class ValueHelper():
    def parse_str_into_python_value(interpreter, value: str) -> BrewinAsPythonValue:
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
            interpreter.interpreter_base.error(ErrorType.NAME_ERROR)

    # For display formatting - convert python value to string
    def convert_python_value_to_str(value: 'Value') -> str:
        from v2_object_def import ObjectDefinition
        if value is True:
            return InterpreterBase.TRUE_DEF
        elif value is False:
            return InterpreterBase.FALSE_DEF
        elif value is None or isinstance(value, ObjectDefinition):
            return "None"
        elif isinstance(value, str):
            return value  # '"' + value + '"'
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))

    # <========= Problem 2: Checking validity of operations =========>
    def is_operand_compatible_with_operator(operator: str, operand: BrewinAsPythonValue) -> bool:
        from v2_object_def import ObjectDefinition
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

    # 1. Get the type of the variable
    def get_variable_type_from_type_str(interpreter, type_str: str):
        if type_str == "int":
            return int
        elif type_str == "string":
            return str
        elif type_str == "bool":
            return bool

        # If not a primitive type, then it must be a class
        # Note: this function will and rightfully error if it can't find it
        return interpreter.find_definition_for_class(type_str)

    # Parameters list comes in as [type_str, argument_name], we need to convert this to a list of types
    def parse_expected_types_from_parameters_list(interpreter, params_list: List[List[str]]) -> List[type]:
        return [ValueHelper.get_variable_type_from_type_str(interpreter, param_type) for param_type, _ in params_list]

    def parse_parameter_names_from_parameters_list(interpreter, params_list: List[List[str]]) -> List[str]:
        parameter_names = []
        duplicate_names = set()

        for param in params_list:
            name = param[1]
            if name in parameter_names:
                duplicate_names.add(name)
            else:
                parameter_names.append(name)

        if duplicate_names:
            raise interpreter.interpreter_base.error(ErrorType.NAME_ERROR)

        return parameter_names

    # TO-DO: Use a better variable naming scheme
    def parse_let_declarations(interpreter, params_list: List[List[str]]) -> Dict[str, str]:
        local_variables = {}
        for param_triple in params_list:
            # Check that the variable hasn't already been added yet
            variable_name: str = param_triple[1]
            if variable_name in local_variables:
                interpreter.interpreter_base.error(ErrorType.NAME_ERROR)

            # Add to map
            return_type_str: str = param_triple[0]
            value_str: str = param_triple[2]
            local_variables[variable_name] = Variable(interpreter, return_type_str, value_str)

        return local_variables
    
    # <===================== STATIC TYPE CHECKING ========================>
    def is_value_compatible_with_variable(value, variable) -> bool:
        from v2_class_def import ClassDefinition

        # Case 1: Primitives
        if variable.type() in [int, str, bool]:
            return value.type() is variable.type()

        # Case 2: Object definition
        # TO-DO: Handle derived objects
        if isinstance(variable.type(), ClassDefinition):
            return value.value() is None or variable.type().class_name == value.type().class_name

        return False
    
    # TO-DO: Remove this
    def is_value_compatible_with_variable_type(value, variable_type) -> bool:
        from v2_class_def import ClassDefinition

        # Case 1: Primitives
        if variable_type in [int, str, bool]:
            return value.type() is variable_type

        # Case 2: Object definition
        # TO-DO: Handle derived objects
        if isinstance(variable_type, ClassDefinition):
            return value.value() is None or variable_type.class_name == value.type().class_name

        return False
    
    # TO-DO: Refactor the logic of this so it's more clear
    def is_value_compatible_with_value(value1, value2) -> bool:
        from v2_object_def import ObjectDefinition
        from v2_class_def import ClassDefinition

        # Case 1: Primitives
        if value1.type() in [int, str, bool] or value2.type() in [int, str, bool]:
            return value1.type() is value2.type()

        # Case 2: Object definition
        # TO-DO: Handle derived objects
        if isinstance(value1.type(), ObjectDefinition) or isinstance(value2.type(), ObjectDefinition) or isinstance(value1.type(), ClassDefinition) or isinstance(value2.type(), ClassDefinition):
            # Handle an unbound null - comparison to with any type is allowed
            # In this case, we are guaranteed that only one of them is a null type
            if value1.type() == None or value2.type() == None:
                return True
            return value1.type().class_name == value2.type().class_name
        # Case 2d - what if both are nulls?
        if value1.type() == None and value2.type() == None:
            return True

        # Case 3: Void return from function
        if value1.type() is NOTHING_TYPE:
            return value2.value() == NOTHING
        if value2.type() is NOTHING_TYPE:
            return value1.type() == NOTHING

        return False

    def is_primitive_type(expected_type) -> bool:
        return expected_type in [int, str, bool]

    def get_return_type_from_type_str(interpreter, type_str):
        if type_str == "int":
            return int
        elif type_str == "string":
            return str
        elif type_str == "bool":
            return bool
        elif type_str == "void":
            return None

        # If not a primitive type, then it must be a class
        # Note: this function will and rightfully error if it can't find it
        return interpreter.find_definition_for_class(type_str)

    def get_default_value_for_return_type(return_type):
        if return_type is int:
            return 0
        elif return_type is str:
            return ''
        elif return_type is bool:
            return False
        # TO-DO: Check the case where nothing is returned vs null object
        else:
            return NOTHING
        
    def get_default_python_value_for_return_type_v2(interpreter, return_type):
        if return_type is int:
            return 0
        elif return_type is str:
            return ''
        elif return_type is bool:
            return False
        # TO-DO: Handle case with the class definition
        # Return type is void
        else:
            return NOTHING

    def get_type_from_value(value: BrewinAsPythonValue) -> type:
        from v2_object_def import ObjectDefinition

        if isinstance(value, bool):
            return bool
        elif isinstance(value, str):
            return str
        elif isinstance(value, int):
            return int
        elif isinstance(value, ObjectDefinition):
            return value.class_def
        # Edge-case: encountered null with no type hint,
        # then it's a generic ObjectDefinition until more info
        elif value is None:
            return None
        # TO-DO: Update this to do the error handling here
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))
        
class Value:
    def __init__(self, interpreter, variable_type: type, python_value: BrewinAsPythonValue):
        self.__interpreter = interpreter
        self.__variable_type = variable_type # This never changes!

        # TO-DO: Fix the naming convention
        self.__value = python_value
        self.__value_type = self.get_type_from_python_value(self.__value)

        # Type check that variable type is compatible with value type
        self.enforce_variable_and_value_type_compatibility(interpreter)

    def get_variable_type(self):
        return self.__variable_type

    # Stage 1 - Used for checking compatibility from constant values
    def enforce_variable_and_value_type_compatibility(self, interpreter):
        if not self.are_variable_and_value_compatible():
            interpreter.interpreter_base.error(ErrorType.TYPE_ERROR)

    # Perform type comparison between variable type and value type
    def are_variable_and_value_compatible(self, value_type=SENTINEL_VALUE) -> bool|None:
        from v2_class_def import ClassDefinition

        if value_type is SENTINEL_VALUE:
            value_type = self.__value_type
        else:
            value_type = value_type

        # Case 1: Primitives - both variable and value type MUST match
        if self.__variable_type in [int, str, bool]:
            return self.__variable_type is value_type

        # Case 2: Object references
        # Variable and value must have SAME or derived class definition
        # For constant expressions - we know that the value has to be none
        if isinstance(self.__variable_type, ClassDefinition):
            # Note if value_type is None - then this is a dangling null
            # Note - the RHS of this fails for polymorphism
            return value_type is None or self.__variable_type.is_other_class_def_same_or_derived_class(value_type)

        # Case 3: Dangling null
        if self.__variable_type is None and value_type is None:
            return True

        # Case 3: The types are not compatible, we should throw an error here
        return False

    def is_compatible_with_other_value(self, other_value: 'Value') -> bool:
        from v2_class_def import ClassDefinition

        # Case 1: Primitives - we just need to know if they are the same type
        if self.get_variable_type() in [int, str, bool] or other_value.get_variable_type() in [int, str, bool]:
            return self.get_variable_type() is other_value.get_variable_type()
        
        # Case 2: Both are object references
        # TO-DO: Update this for polymorphism
        if isinstance(self.get_variable_type(), ClassDefinition) and isinstance(other_value.get_variable_type(), ClassDefinition):
            return self.get_variable_type().class_name == other_value.get_variable_type().class_name
        
        # Case 3: At least one of them is a dangling null
        if self.get_variable_type() == None or other_value.get_variable_type() == None:
            return True
        
        # Case 4: The types are not compatible
        # TO-DO: Maybe throw an error here?
        return False

    # Stage 2 - Updating Value over time:
    # Evaluate expression will give us the correct Value for us to use
    def set_value_to_other_checked(self, interpreter, new_program_value: 'Value') -> None:
        program_value = new_program_value.value()
        program_type = new_program_value.type()

        # Before setting value, perform a type check
        if not self.are_variable_and_value_compatible(program_type):
            interpreter.interpreter_base.error(ErrorType.TYPE_ERROR)

        self.__value = program_value
        self.__value_type = program_type

    # TO-DO: Remove the other declaration of this function befoer it gets too confusing
    def get_type_from_python_value(self, evaluated_value: BrewinAsPythonValue) -> type|None:
        from v2_object_def import ObjectDefinition

        if isinstance(evaluated_value, bool):
            return bool
        elif isinstance(evaluated_value, str):
            return str
        elif isinstance(evaluated_value, int):
            return int
        # A new object reference was created in this process
        # The type will be its class definition
        elif isinstance(evaluated_value, ObjectDefinition):
            return evaluated_value.class_def
        # Edge case - dangling null value
        else:
            return None

    # <======== Getters & setters ==========>
    def type(self):
        # TO-DO: Should this refer to value type or variable type?
        return self.__value_type

    def value(self):
        return self.__value

    def set(self, other):
        self.__type = other.type()
        self.__value = other.value()

    # def set_value_to_other(self, other):
    #     self.__value = other.value()

class Variable:
    """A representation for a variable that contains a value and type tag"""
    def __init__(self, interpreter, type_str: str, value_str: str, type_override=None, program_value_override=None):
        self.__interpreter = interpreter

        # TO-DO: Fix Antipattern 
        if type_override:
            self.__variable_type = type_override
        else:
            self.__variable_type: type = self.get_variable_type_from_type_str(type_str) # Step 2

        # TO-DO: Fix antipattern
        if program_value_override:
            self.__program_value = program_value_override
        else:
            python_value = ValueHelper.parse_str_into_python_value(interpreter, value_str)
            self.__program_value: Value = Value(interpreter, self.__variable_type, python_value) # Step 3, 5
 
    # <======== Stage 1 - Instantiating a new value ==========>
    # 1. Get the type of the variable
    def get_variable_type_from_type_str(self, type_str: str):
        if type_str == "int":
            return int
        elif type_str == "string":
            return str
        elif type_str == "bool":
            return bool

        # If not a primitive type, then it must be a class
        # Note: this function will and rightfully error if it can't find it
        return self.__interpreter.find_definition_for_class(type_str)

    def value(self) -> Value:
        return self.__program_value

    # # Type-checked update of the value
    # def update_value_checked(self, value: Value):
    #     if not self.__is_value_compatible(value):
    #         self.__interpreter.interpreter_base.error(ErrorType.TYPE_ERROR)

    #     # Update the value
    #     self.set_program_value(value)

    # def set_program_value(self, value: Value):
    #     self.__program_value = value
