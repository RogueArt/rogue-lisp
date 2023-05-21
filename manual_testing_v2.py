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


    # Valid case for calling a method with argument types
    call_with_valid_argument_types = [
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

    # Valid case for calling a method with argument types
    # Expect a type error
    call_with_invalid_argument_types = [
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
    '(call me print_stuff y y p)',
    ')',
    '(method void print_stuff ((int a) (string b) (person p))',
    '(print a " " b " " p)', # Note - we aren't expected to print the person object, but do it for testing anyways
    ')',
    ')'
    ]

    # Test default return types
    call_with_invalid_argument_types = [
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
    '(call me print_stuff y y p)',
    ')',
    '(method void print_stuff ((int a) (string b) (person p))',
    '(print a " " b " " p)', # Note - we aren't expected to print the person object, but do it for testing anyways
    ')',
    ')'
    ]

    call_with_valid_default_types = [
  '(class person',
  '(method void nothing ()',
  '(print "")',
  ')',
  ')',
  '(class main',
  '(method int default_int ()',
  '(return)',
  ')',
  '(method string default_string ()',
  '(return)',
  ')',
  '(method bool default_bool ()',
  '(return)',
  ')',
  '(method person default_person ()',
  '(return)',
  ')',
  '(method void main ()',
  '(begin',
  '(print (call me default_int) " " (call me default_string) " " (call me default_bool) " " (call me default_person))',
  ')',
  ')',
  ')'
]

    # Simple valid case - one level variable case
    valid_local_variables_with_let = [
  '(class main',
  '(method void foo ()',
  '(begin',
  '(let ((int y 5))',
  '(print y)\t\t# this prints out 5',
  ')',
  ')',
  ')',
  '(method void main ()',
  '(call me foo)',
  ')',
  ')'
]
    
    # Invalid case - trying to access local variable outside of where it's declared
    invalid_local_variable_access_with_let = [
  '(class main',
  '(method void foo ()',
  '(begin',
  '(let ((int y 5))',
  '(print y)\t\t# this prints out 5',
  ')',
  '(print y)',
  ')',
  ')',
  '(method void main ()',
  '(call me foo)',
  ')',
  ')'
]
    let_with_shadowing_test = [
  '(class main',
  '(method void foo ((int x))',
  '(begin',
  '(print x)  \t\t\t\t\t# Line #1: prints 10',
  '(let ((bool x true) (int y 5))',
  '(print x)\t\t\t\t\t# Line #2: prints true',
  '(print y)\t\t\t\t\t# Line #3: prints 5',
  ')',
  '(print x)\t\t\t\t\t# Line #4: prints 10',
  ')',
  ')',
  '(method void main ()',
  '(call me foo 10)',
  ')',
  ')'
]
    
    let_with_nested_shadowing_test = [
  '(class main',
  '(method void foo ((int x))',
  '(begin',
  '(print x)  \t\t\t\t\t# Line #1: prints 10',
  '(let ((bool x true) (int y 5))',
  '(let ((bool x false) (int y 100))',
  '(print x)\t\t\t\t\t# Line #2: prints false',
  '(print y)\t\t\t\t\t# Line #3: prints 100',
  ')',
  ')',
  '(print x)\t\t\t\t\t# Line #4: prints 10',
  ')',
  ')',
  '(method void main ()',
  '(call me foo 10)',
  ')',
  ')'
    ]

    let_with_nested_shadowing_test_multiple_class = [
  '(class person',
  '(method void foo ((int x))',
  '(begin',
  '(print x)  \t\t\t\t\t# Line #1: prints 10',
  '(let ((bool x true) (int y 5))',
  '(let ((string x "hello") (int y 100))',
  '(print x)\t\t\t\t\t# Line #2: prints hello',
  '(print y)\t\t\t\t\t# Line #3: prints 100',
  ')',
  '(print x)                    # Line #4: prints true',
  ')',
  '(print x)\t\t\t\t\t# Line #5: prints 10',
  ')',
  ')',
  ')',
  '(class main',
  '(field person p null)',
  '(method void main ()',
  '(begin',
  '(set p (new person))',
  '(call p foo 10)',
  ')',
  ')',
  ')'
]
    
    let_with_nothing = [
  '(class person',
  '(method void foo ((int x))',
  '(begin',
  '(print x)  \t\t\t\t\t# Line #1: prints 10',
  '(let ()',
  '(print "hello")',
  ')',
  '(print x)\t\t\t\t\t# Line #5: prints 10',
  ')',
  ')',
  ')',
  '(class main',
  '(field person p null)',
  '(method void main ()',
  '(begin',
  '(set p (new person))',
  '(call p foo 10)',
  ')',
  ')',
  ')'
]
    
    # No method calls - allows us to check if inheritance chains are being built correctly
    inheritance_chain_test = """
# Machine
# Animal -> Person 
#		|        | -> Nerd
#		|        | -> Student
#       | -> Dog -> GoldenRetriever

(class machine (method void main () (return)))

(class animal (method void main () (return)))
  (class person inherits animal (method void main () (return)))
    (class nerd inherits person (method void main () (return)))
    (class student inherits person (method void main () (return)))
  (class dog inherits animal (method void main () (return)))
      (class goldenretriever inherits dog (method void main () (return)))

(class main
  (method void main ()
    (begin
      (print "Sanity check for inheritance chains")
    )
  )
)




    """.split('\n')
    
    basic_inheritance = """
    (class person
  (field string name "anonymous")
  (method void set_name ((string n)) (set name n))
  (method void say_something () (print name " says hi"))
)

(class student inherits person
  (field int student_id 0)
  (method void set_id ((int id)) (set student_id id))
  (method void say_something ()
    (begin
     (print "first")
     (call super say_something)  # calls person's say_something method
     (print "second")
    )
  )
)

(class main
  (field student s null)
  (method void main ()
    (begin
      (set s (new student))
      (call s set_name "julin")   # calls person's set_name method
(call s set_id 010123456) # calls student's set_id method
      (call s say_something)	  # calls student's say_something method
    )
  )
)

    """.split('\n')
    

    return {
        "field_and_method_types": field_and_method_types,
        "set_valid_field_types": set_valid_field_types,

        # Exception tests
        "set_string_on_int_field": set_string_on_int_field,
        "set_int_on_string_field": set_int_on_string_field,
        "set_object_on_primitive_field": set_object_on_primitive_field,

        "call_with_valid_argument_types": call_with_valid_argument_types,
        "call_with_invalid_argument_types": call_with_invalid_argument_types,
        "call_with_valid_default_types": call_with_valid_default_types,

        "valid_local_variables_with_let": valid_local_variables_with_let,
        'invalid_local_variable_access_with_let': invalid_local_variable_access_with_let,
        'let_with_shadowing_test': let_with_shadowing_test,
        'let_with_nested_shadowing_test': let_with_nested_shadowing_test,
        'let_with_nested_shadowing_test_multiple_class': let_with_nested_shadowing_test_multiple_class,
        'let_with_nothing': let_with_nothing,

        'basic_inheritance': basic_inheritance,
        'inheritance_chain_test': inheritance_chain_test
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