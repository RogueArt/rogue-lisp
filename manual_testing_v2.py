#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Dict
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint


# DEBUGGING ONLY - PLEASE DO NOT PUSH:

def get_test_programs():
    # Legacy test - Verify that program with field types can be parsed (legacy)
#     field_types = [
#   '(class person',
#   '(method nothing ()',
#   '(return "")',
#   ')',
#   ')',
#   '(class main',
#   '(field int x 10)',
#   '(field string y "xyz")',
#   '(field person p null)',
#   '(method main ()',
#   '(print x " " y)',
#   ')',
#   ')'
# ]


    # Verify parsing of return and parameter types
    # Expected output: 10 xyz null
    # Note: we can't break this down further as `void` needs to be recognized
    field_and_method_types = [
    '(class person',
    '(method void nothing ()',
    '(return "")',
    ')',
    ')',
    '(class main',
    '(field int x 10)',
    '(field string y "xyz")',
    '(field person p null)',
    '(method void main ()',
    '(print x " " y " " p " " (% 3 2))',
    ')',
    ')'
    ]

    # Verify setting values that are valid for the type
    # Expected output: 3 hello null
    set_valid_field_types = [
  '(class person',
  '(method void say_something ()',
  '(return "")',
  ')',
  ')',
  '(class main',
  '(field int x 10)',
  '(field string y "xyz")',
  '(field person p null)',
  '(method void main ()',
  '(call me print_stuff 3 "hello")',
  ')',
  '(method void print_stuff ((int a) (string b))',
  '(begin',
  '(set x 3)',
  '(set y "hello")',
  '(set p (new person))',
  '(print x " " y " " p)',
  ')',
  ')',
  ')'
]
    
    # Expect a type error for each of these
    set_string_on_int_field = [
        '(class person',
        '(method void say_something ()',
        '(return "")',
        ')',
        ')',
        '(class main',
        '(field int x 10)',
        '(field string y "xyz")',
        '(field person p null)',
        '(method void main ()',
        '(call me print_stuff 3 "hello")',
        ')',
        '(method void print_stuff ((int a) (string b))',
        '(begin',
        '(set x "hello")',
        # '(set y "hello")',
        # '(set p (new person))',
        '(print x " " y " " p)',
        ')',
        ')',
        ')'
    ]
    # Expect a type error for each of these
    set_int_on_string_field = [
        '(class person',
        '(method void say_something ()',
        '(return "")',
        ')',
        ')',
        '(class main',
        '(field int x 10)',
        '(field string y "xyz")',
        '(field person p null)',
        '(method void main ()',
        '(call me print_stuff 3 "hello")',
        ')',
        '(method void print_stuff ((int a) (string b))',
        '(begin',
        # '(set x "hello")',
        '(set y 3)',
        # '(set p (new person))',
        '(print x " " y " " p)',
        ')',
        ')',
        ')'
    ]
    # Expect a type error for each of these
    set_object_on_primitive_field = [
        '(class person',
        '(method void say_something ()',
        '(return "")',
        ')',
        ')',
        '(class main',
        '(field int x 10)',
        '(field string y "xyz")',
        '(field person p null)',
        '(method void main ()',
        '(call me print_stuff 3 "hello")',
        ')',
        '(method void print_stuff ((int a) (string b))',
        '(begin',
        # '(set x "hello")',
        # '(set y 3)',
        '(set x (new person))',
        '(print x " " y " " p)',
        ')',
        ')',
        ')'
    ]


    # Argument type parsing
    argument_types = [
    '(class person',
    '(method void nothing ()',
    '(return "")',
    ')',
    ')',
    '(class main',
    '(field int x 10)',
    '(field string y "xyz")',
    '(field person p null)',
    '(method void main ()',
    '(call me print_stuff x y p)',
    ')',
    '(method void print_stuff ((int a) (string b) (person p))',
    '(print a " " b " " p)', # Note - we aren't expected to print the person object, but do it for testing anyways
    ')',
    ')'
    ]
    
    method_types_with_obj = [
  '(class person',
  '(method void nothing ()',
  '(return "")',
  ')',
  ')',
  '(class main',
  '(field int x 10)',
  '(field string y "xyz")',
  '(field person p null)',
  '(method void main ()',
  '(call me print_stuff x y)',
  ')',
  '(method void print_stuff ((int a) (string b) (person p))',
  '(print a " " b)',
  ')',
  ')'
]


    return {
        "field_and_method_types": field_and_method_types,
        "set_valid_field_types": set_valid_field_types,

        # Exception tests
        # "set_string_on_int_field": set_string_on_int_field,
        # "set_int_on_string_field": set_int_on_string_field,
        # "set_object_on_primitive_field": set_object_on_primitive_field
    }
# Deliberately small and obscure name for each easy debugging
# Will pretty print the array with the given indentation level

def fn(items, level=-1):
    for item in items:
        if isinstance(item, list):
            fn(item, level + 1)
        else:
            indentation = '    ' * level
            print('%s%s' % (indentation, item))