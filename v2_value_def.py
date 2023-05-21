from intbase import InterpreterBase, ErrorType
from v2_constants import *


# TO-DO: Make this implementation less jank
NOTHING='NOTHING_SDLKFJSDFKJ'

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
    def convert_python_value_to_str(value: BrewinAsPythonValue) -> str:
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

    def is_operand_compatible_with_operand(operand1: BrewinAsPythonValue, operand2: BrewinAsPythonValue) -> bool:
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
            # Parse type, value, and name
            return_type: type = ValueHelper.get_variable_type_from_type_str(interpreter, param_triple[0])
            variable_name: str = param_triple[1]
            value = ValueHelper.parse_str_into_python_value(interpreter, param_triple[2])
            
            field_value = { 'type': ValueHelper.get_type_from_value(value), 'value': value }

            # Type check the value with the parameter type before adding to map
            if not ValueHelper.is_value_compatible_with_variable(field_value, { 'type': return_type }):
                interpreter.interpreter_base.error(ErrorType.TYPE_ERROR)

            # Check that the variable hasn't already been added yet
            if variable_name in local_variables:
                interpreter.interpreter_base.error(ErrorType.NAME_ERROR)

            # Add to map
            local_variables[variable_name] = { 'type': return_type, 'value': value }

        return local_variables
    
    # <===================== STATIC TYPE CHECKING ========================>
    def is_value_compatible_with_variable(value, variable) -> bool:
        from v2_class_def import ClassDefinition

        # Case 1: Primitives
        if variable['type'] in [int, str, bool]:
            return value['type'] is variable['type']

        # Case 2: Object definition
        # TO-DO: Handle derived objects
        if isinstance(variable['type'], ClassDefinition):
            return value['value'] is None or variable['type'].class_name == value['type'].class_name

        # Case 3: Void variable
        if variable['type'] is None:
            return value['value'] is None
        
        return False
    
    def is_value_compatible_with_value(value1, value2) -> bool:
        from v2_object_def import ObjectDefinition
        from v2_class_def import ClassDefinition

        # Case 1: Primitives
        if value1['type'] in [int, str, bool] or value2['type'] in [int, str, bool]:
            return value1['type'] is value2['type']

        # Case 2: Object definition
        # TO-DO: Handle derived objects
        if isinstance(value1['type'], ObjectDefinition) or isinstance(value2['type'], ObjectDefinition) or isinstance(value1['type'], ClassDefinition) or isinstance(value2['type'], ClassDefinition):
            # Handle an unbound null - comparison to with any type is allowed
            if value1['type'] == NOTHING or value2['type'] == NOTHING:
                return True
            return value1['type'].class_name == value2['type'].class_name
        
        return False

    def is_primitive_type(expected_type) -> bool:
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
        
    def get_type_from_value(value: BrewinAsPythonValue) -> type:
        from v2_object_def import ObjectDefinition

        if isinstance(value, bool):
            return bool
        elif isinstance(value, str):
            return str
        elif isinstance(value, int):
            return int
        elif isinstance(value, ObjectDefinition):
            return value
        # Edge-case: encountered null with no type hint,
        # then it's a generic ObjectDefinition until more info
        elif value is None:
            return NOTHING
        # TO-DO: Remove this
        else:
            raise ValueError('Unsupported value type: {}'.format(type(value)))

class Value:
    """A representation for a value that contains a type tag."""

    def __init__(self, value_type, value=None):
        self.__type = value_type
        self.__value = value

    def type(self):
        return self.__type

    def value(self):
        return self.__value

    def set(self, other):
        self.__type = other.type()
        self.__value = other.value()
