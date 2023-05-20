# from bparser import BParser
# from intbase import InterpreterBase
# from v2_object_def import *

# import copy

# class ClassDefinition:
#     # constructor for a ClassDefinition
#     def __init__(self, interpreter, interpreter_base: InterpreterBase, name, methods, fields):
#         self.interpreter = interpreter
#         self.interpreter_base = interpreter_base
#         self.name = name
#         self.methods = methods
#         self.fields = fields

#     # uses the definition of a class to create and return an instance of it
#     def instantiate_object(self):
#         obj = ObjectDefinition(self.interpreter, self.interpreter_base, 
#                                copy.deepcopy(self.methods), copy.deepcopy(self.fields))
#         return obj
