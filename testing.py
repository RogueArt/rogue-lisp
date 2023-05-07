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

    # Parameter other call test - be able to call a method in another class with parameters on it
    parameter_other_call_test = [
        '(class animal',
        '(method speak (type age sound)',
        '(print "I am a " type " who is " age " year(s) old and goes " sound)',
        ')',
        ')',
        '(class main',
        '(field animal_ref null)',
        '(method main ()',
        '(begin',
        '(set animal_ref (new animal))',
        '(call animal_ref speak "dog" 20 "woof!")',
        ')',
        ')',
        ')'
    ]

    # Parameter scoping test - be able to call a method in another class with parameters in it
    # Tests three different cases
    # 1. Value is present in parameter only
    # 2. Value is present in field only
    # 3. Value in both parameter and field, parameter takes precedence
    parameter_scoping_test = [
        '(class animal',
        '(field type "unknown")',
        '(field age 20)',
        '(method speak (type sound)',
        '(print "I am a " type " who is " age " year(s) old and goes " sound)',
        ')',
        ')',
        '(class main',
        '(field animal_ref null)',
        '(method main ()',
        '(begin',
        '(set animal_ref (new animal))',
        '(call animal_ref speak "dog" "woof!")',
        ')',
        ')',
        ')'
    ]

    # Recursion test - be able to repeatedly call a method in a class until we hit a base case

    return {'simple': simple, 'many_fields': many_fields, 'simple_begin_test': simple_begin_test, 'nested_begin_test': nested_begin_test, 'set_fields': set_fields,
            'basic_other_call_test': basic_other_call_test, 'basic_self_call_test': basic_self_call_test, 'parameter_other_call_test': parameter_other_call_test, 'parameter_scoping_test': parameter_scoping_test}

# Deliberately small and obscure name for each easy debugging
# Will pretty print the array with the given indentation level


def fn(items, level=-1):
    for item in items:
        if isinstance(item, list):
            fn(item, level + 1)
        else:
            indentation = '    ' * level
            print('%s%s' % (indentation, item))
