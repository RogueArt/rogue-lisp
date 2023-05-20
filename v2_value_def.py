# from intbase import InterpreterBase, ErrorType
# from v2_class_def import ClassDefinition
# from v2_object_def import ObjectDefinition

# class ValueHelper():
#     def parse_str_into_python_value(value: str) -> None | int | bool | str:
#       if value == InterpreterBase.TRUE_DEF:
#           return True
#       elif value == InterpreterBase.FALSE_DEF:
#           return False
#       elif value == InterpreterBase.NULL_DEF:
#           return None
#       elif isinstance(value, str) and value[0] == '"' and value[-1] == '"':
#           return value[1:-1]
#       elif value.lstrip('-').isnumeric():
#           return int(value)
#       else:
#           InterpreterBase.error(ErrorType.NAME_ERROR)

#     # For display formatting - convert python value to string
#     def convert_python_value_to_str(value) -> str:
#         if value is True:
#             return InterpreterBase.TRUE_DEF
#         elif value is False:
#             return InterpreterBase.FALSE_DEF
#         elif value is None:
#             return InterpreterBase.NULL_DEF
#         elif isinstance(value, str):
#             return value # '"' + value + '"'
#         elif isinstance(value, int):
#             return str(value)
#         else:
#             raise ValueError('Unsupported value type: {}'.format(type(value)))
        
#     def is_operand_compatible_with_operator(operator: str, operand) -> bool:
#         if isinstance(operand, str) and operator == '+':
#             return True  # String concatenation is allowed with the + operator
#         elif type(operand) is int and operator in ['+', '-', '*', '/', '%']:
#             return True  # Integer arithmetic is allowed with the +, -, *, /, and % operators
#         elif isinstance(operand, int) and operator in ['<', '>', '<=', '>=', '!=', '==']:
#             return True  # Integer comparison is allowed with the <, >, <=, >=, !=, and == operators
#         elif isinstance(operand, str) and operator in ['<', '>', '<=', '>=', '!=', '==']:
#             return True  # String comparison is allowed with the <, >, <=, >=, !=, and == operators
#         elif isinstance(operand, bool) and operator in ['&', '|', '==', '!=']:
#             return True  # Boolean comparison is allowed with the & (AND), | (OR), ==, and != operators
#         elif operand is None and operator in ['==', '!=']:
#             return True  # Null comparison is allowed with the == and != operators
#         elif isinstance(operand, ObjectDefinition) and operator in ['==', '!=']:
#             return True # Object comparison is allowed with the == and != operators 
#         elif operator == '!':
#             return isinstance(operand, bool)  # Unary NOT is only allowed with booleans
#         else:
#             return False  # Operand and operator are not compatible
  
#     def is_operand_compatible_with_operand(operand1, operand2) -> bool:
#       # If both operands are primitives, then if types don't match, not compatible
#       if ValueHelper.is_primitive_type(operand1) and ValueHelper.is_primitive_type(operand2):
#           return type(operand1) == type(operand2)

#       # Object definition type - can be None or Class
#       return True      

#     # In Brewin, string, int, and bool are primitive types
#     def is_primitive_type(value):
#         return isinstance(value, str) or isinstance(value, int) or isinstance(value, bool)
    
#     # <===================== STATIC TYPE CHECKING ========================>
#     def does_type_declaration_match_value(parsed_type: type, value: int|bool|str|None|ObjectDefinition) -> bool:
#         # Case 1 - Primitives
#         if ValueHelper.is_primitive_type(parsed_type):
#             return type(value) == parsed_type

#         # Case 2 - Object definition
#         # TO-DO: Handle derived objects
#         # parsed_type will give us Person
#         # if we have None, that's chill
#         # if we get Parse, that's also fine
#         if isinstance(parsed_type, ClassDefinition):
#             return value is None or isinstance(value, parsed_type)

#         # Case 3
#         return False


#     def is_primitive_type(expected_type):
#         return expected_type in [int, str, bool]

#     def get_variable_type_from_type_str(interpreter, type_str: str):
#         if type_str == "int":
#             return int
#         elif type_str == "string":
#             return str
#         elif type_str == "bool":
#             return bool

#         # If not a primitive type, then it must be a class
#         return interpreter.find_definition_for_class(type_str)

#     def get_return_type_from_type_str(interpreter, type_str):
#         if type_str == 'void':
#             return None
#         else:
#             return ValueHelper.get_variable_type(interpreter, type_str)
