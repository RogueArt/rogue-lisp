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
                   '(method main () (print "The value is " foo_123 " and " name " and " _awesome " and " obj_ref_field_puppy " and value is " (% 3 2)))',
                   ')']

    # Begin test - prints 3 different statements in a row, building on top of hello world
    simple_begin_test = ['(class main',
                         '(field foo_123 10)',
                         '(field name "unknown")',
                         '(field _awesome true)',
                         '(field obj_ref_field_puppy null)',
                         '(method main () (begin',
                         '(print "foo_123 is " foo_123)',
                         '(print "name is " name)',
                         '(print "_awesome is " _awesome)'
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
                         '(print "foo_123 is " foo_123)',
                         ')',
                         '(begin'
                         '(begin'
                         '(begin'
                         '(print "name is " name)',
                         '(print "_awesome is " _awesome)'
                         'begin',
                         ')'
                         ')',
                         ')',
                         ')',
                         '))']

    # Set test - builds on top of begin & fields test
    # Additionally tests object instantiation as well
    set_fields = ['(class puppy', '(method bark ()', '(print "woof!")', ')', ')', '(class main', '(field foo_123 10)', '(field name "unknown")', '(field _awesome true)', '(field obj_ref_field_puppy null)', '(method main ()',
                  '(begin', '(set foo_123 (+ 20 50))', '(set name true)', '(set _awesome 0)', '(set obj_ref_field_puppy (new puppy))' '(print "The value is " foo_123 " and " name " and " _awesome " and value is " (% 3 2)))', ')', ')']

    # Basic call test - be able to instantiate object and call a method with no parameters on it
    basic_other_call_test = ['(class puppy', '(method bark ()', '(print "woof!")', ')', ')', '(class main', '(field puppy_ref null)',
                       '(method main ()', '(begin', '(set puppy_ref (new puppy))', '(call puppy_ref bark)', ')', ')', ')']

    # Basic self call test - be able to call a method from own class
    basic_self_call_test = ['(class main', '(method bark () (print "its a me, mario!"))',
                       '(field puppy_ref null)', '(method main ()', '(begin', '(call me bark)', ')', ')', ')']
    
    # Nested call test - be able to call a method from own class

    return {'simple': simple, 'many_fields': many_fields, 'simple_begin_test': simple_begin_test, 'nested_begin_test': nested_begin_test, 'basic_other_call_test': basic_other_call_test, 'basic_self_call-test': basic_self_call_test, 'set_fields': set_fields}

# Deliberately small and obscure name for each easy debugging
# Will pretty print the array with the given indentation level


def fn(items, level=-1):
    for item in items:
        if isinstance(item, list):
            fn(item, level + 1)
        else:
            indentation = '    ' * level
            print('%s%s' % (indentation, item))
