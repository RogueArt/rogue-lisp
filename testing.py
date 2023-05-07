from typing import List, Dict
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint

# DEBUGGING ONLY - PLEASE DO NOT PUSH:


def get_test_programs():
    # Hello world - `main()` method that prints "hello world"
    simple = [
        '(class main', '(method main ()', '(print "Hello world!")', ')', ')']

    # Fields test - Many different fields of different types, print out all of them
    many_fields = ['(class main',
                   '(field foo_123 10)',
                   '(field name "unknown")',
                   '(field _awesome true)',
                   '(field obj_ref_field_puppy null)',
                   '(method main () (print "The value is" foo_123 "and" name "and" _awesome "and" obj_ref_field_puppy (% 3 2)))',
                   ')']

    # Begin test - prints 3 different statements in a row, building on top of hello world
    simple_begin_test = ['(class main',
                  '(field foo_123 10)',
                  '(field name "unknown")',
                  '(field _awesome true)',
                  '(field obj_ref_field_puppy null)',
                  '(method main () (begin',
                  '(print "foo_123 is" foo_123)',
                  '(print "name is" name)',
                  '(print "_awesome is" _awesome)'
                  ')',
                  '))']

    # Nested begin test - prints 3 different statements in a row
    # Same as the simple one, but now there are nested begin statements
    nested_begin_test = ['(class main',
                         '(field foo_123 10)',
                         '(field name "unknown")',
                         '(field _awesome true)',
                         '(field obj_ref_field_puppy null)',
                         '(method main () (begin',
                         '(begin'
                         '(print "foo_123 is" foo_123)',
                         ')',
                         '(begin'
                         '(begin'
                         '(begin'
                         '(print "name is" name)',
                         '(print "_awesome is" _awesome)'
                         'begin',
                         ')'
                         ')',
                         ')',
                         ')',
                         '))']

    # Set test - builds on top of begin & fields test, but additionally also call object instantiation
    set_fields = ['(class main', '(field foo_123 10)', '(field name "unknown")', '(field _awesome true)', '(field obj_ref_field_puppy null)', '(method main ()',
                  '(begin', '(set foo_123 (+ 20 50))', '(set name true)', '(set _awesome 0)', '(set obj_ref_field_puppy (new puppy))' '(print "The value is" foo_123 "and" name "and" _awesome "and" obj_ref_field_puppy (% 3 2)))', ')', ')']

    return {'simple': simple, 'many_fields': many_fields, 'simple_begin_test': simple_begin_test, 'nested_begin_test': nested_begin_test, 'set_fields': set_fields}

# Deliberately small and obscure name for each easy debugging
# Will pretty print the array with the given indentation level


def fn(items, level=-1):
    for item in items:
        if isinstance(item, list):
            fn(item, level + 1)
        else:
            indentation = '    ' * level
            print('%s%s' % (indentation, item))
