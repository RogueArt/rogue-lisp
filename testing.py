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

    # Integer comparison
    integer_comparison = [
    '(class main',
    '(field some_object null)',
    '(method main ()',
    '(begin',
        '(print "(+ 5 10) " (+ 5 10))           # 15',
        '(print "(+ -5 10) " (+ -5 10))         # 5',
        '(print "(+ 5 0) " (+ 5 0))             # 5',
        '(print "(+ -5 -10) " (+ -5 -10))       # -15',
        '(print "(- 5 10) " (- 5 10))           # -5',
        '(print "(- -5 10) " (- -5 10))         # -15',
        '(print "(- 5 0) " (- 5 0))             # 5',
        '(print "(- -5 -10) " (- -5 -10))       # 5',
        '(print "(* 5 10) " (* 5 10))           # 50',
        '(print "(* -5 10) " (* -5 10))         # -50',
        '(print "(* 5 0) " (* 5 0))             # 0',
        '(print "(* -5 -10) " (* -5 -10))       # 50',
        '(print "(/ 10 5) " (/ 10 5))           # 2',
        '(print "(/ -10 5) " (/ -10 5))         # -2',
        # '(print "(/ 5 0) " (/ 5 0))             # error',
        '(print "(/ -10 -5) " (/ -10 -5))       # 2',
        '(print "(% 10 3) " (% 10 3))           # 1',
        '(print "(% -10 3) " (% -10 3))         # 2',
        # '(print "(% 5 0) " (% 5 0))             # error',
        '(print "(% -10 -3) " (% -10 -3))       # -1',
        '(print "(> 5 5) " (> 5 5))           # false',
        '(print "(> 10 5) " (> 10 5))         # true',
        '(print "(< -5 5) " (< -5 5))         # true',
        '(print "(< 0 -10) " (< 0 -10))       # false',
        '(print "(<= 5 5) " (<= 5 5))         # true',
        '(print "(<= -5 5) " (<= -5 5))       # true',
        '(print "(>= 5 5) " (>= 5 5))         # true',
        '(print "(>= 10 -5) " (>= 10 -5))     # true',
        '(print "(== 5 5) " (== 5 5))         # true',
        '(print "(== -5 -5) " (== -5 -5))     # true',
        '(print "(!= 5 5) " (!= 5 5))         # false',
        '(print "(!= -5 5) " (!= -5 5))       # true',
    ')',
    ')',
    ')'
]


    # Boolean comparison
    boolean_comparison = [
        '(class main',
        '(field some_object null)',
        '(method main ()',
        '(begin',
            '(print "(+ 10 5) " (+ 10 5))          # 15',
            '(print "(> 10 5) " (> 10 5))          # true',
            '(print "(+ hello world) " (+ "hello" "world"))    # helloworld',
            '(print "(>= foo bar) " (>= "foo" "bar"))       # true',
            '(print "(& true false) " (& true false))      # false',
            '(print "(== some_object null) " (== some_object null))   # true',
            '(print "(! false) " (! false))          # true',
            '(print "(& true true) " (& true true))      # true',
            '(print "(& true false) " (& true false))     # false',
            '(print "(| false false) " (| false false))    # false',

            # Do NOT allow null and boolean to be made into a comparison
            # '(print "(| null false) " (| null false))    # error',
            # Do NOT allow unary comparison with null / None
            # '(print "(! null) " (! null))    # error',

            # Nested case
            '(print "(| (& true false) (! some_object))) " (| (& true false) (! false)))    # false',
            '(print "(| true false)) " (| true false))     # true',
            '(print "(! true)) " (! true))           # false',
            '(print "(! false)) "(! false))          # true',
            '(print "(== true true)) " (== true true))     # true',
            '(print "(== true false)) " (== true false))    # false',
            '(print "(!= false true)) " (!= false true))    # true',
            '(print (! (! false)))',
        ')',
        ')',
        ')'
    ]

    # String comparison
    string_comparison = [
        '(class main',
        '(field some_object null)',
        '(method main ()',
        '(begin',
        '(print "(== hello hello) " (== "hello" "hello"))',   # true
        '(print "(== hello world) " (== "hello" "world"))',  # false
        '(print "(!= hello world) " (!= "hello" "world"))',  # true
        '(print "(< apple banana) " (< "apple" "banana"))',   # true
        '(print "(<= banana banana) " (<= "banana" "banana"))', # true
        '(print "(> dog cat) " (> "dog" "cat"))',         # true
        '(print "(>= cat bat) " (>= "cat" "bat"))',        # true
        ')',
        ')',
        ')'
    ]

    # Null comparison
    null_comparison = [
        '(class main',
        '(field object null)'
        '(method main ()',
        '(begin',
        '(print "(== null object) " (== null object))',   # true
        '(print "(!= null object) " (!= null object))',   # false
        '(set object (new main))',
        '(print "Object is now non-null")'
        '(print "(== null object) " (== null object))', # false
        '(print "(!= null object) " (!= null object))',   # true
        ')',
        ')',
        ')'
    ]

    # Note that the strings inside the parentheses are now double-quoted, without any escape characters, and the parentheses themselves are enclosed in single quotes.

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

    # If statement - If (expr) (statement) variant
    if_statement = [
        '(class main',
        '(method main ()',
        '(begin',
        '# Success case - print the value',
        '(if (> (+ 3 2) 0)',
        '(print "5 is greater than 0!")',
        ')',
        "# Failure case - don't print value",
        '(if (>= -20 (/ 10 2))',
        '(print "-20 is not greater than 5!")',
        ')',
        ')',
        ')',
        ')'
    ]

    # If else statement - If (expr) (statementA) (statementB)
    if_else_statement = [
        '(class main',
        '(method main ()',
        '(begin',
        '# Success case - print the value',
        '(if (> (+ 3 2) 0)',
        '(print "5 is greater than 0!")',
        '(print "5 is not greater than 0!")',
        ')',
        "# Failure case - don't print value",
        '(if (>= -20 (/ 10 2))',
        '(print "-20 is greater than or equal to 5!")',
        '(print "-20 is not greater than or equal to 5!")',
        ')',
        ')',
        ')',
        ')'
    ]

    # Whlie statement - False case - should never execute
    while_statement_false = [
        '(class main',
        '(method main ()',
        '(begin',
        '(while (< 1 0)',
        '(begin',
        '(print "x is " x)',
        '(set x (- x 1))',
        ')',
        ')',
        ')',
        ')',
        ')'
    ]

    # While statement - True case - looping count down
    while_statement_return = [
        '(class main',
        '(method foo (q)',
        '(while (> q 0)',
        '(begin'
        '(if (== (% q 3) 0)',
        '(return)  # immediately terminates loop and function foo',
        '(set q (- q 1))',
        ')',
        '(print "Comparison value is: " (% q 3))',
        ')',
        ')',
        ')',
        '(method main ()',
        '(print (call me foo 5))',
        ')',
        ')'
        ]

    # Nested while s tatement - True case - looping count down

    # Test that int and str can successfully receive inputs
    input_int_test = [
        '(class main',
        '(field x 0)',
        '(method main ()',
        '(begin',
        '(print "Please enter a number: ")'
        '(inputi x) # input value from user, store in x variable',
        '(print "3 more than what the user typed in is " (+ x 3))',
        ')',
        ')',
        ')'
    ]

    # Same as above, but with strings and concatenation this time
    input_str_test = [
        '(class main',
        '(field x "player unknowns battlegrounds")',
        '(method main ()',
        '(begin',
        '(print "Please enter your favorite game: ")'
        '(inputs x) # input value from user, store in x variable',
        '(print (+ "The user\'s favorite game is: " x))',
        ')',
        ')',
        ')'
    ]

    # Non-control flow return - regular return statement to test evaluating expressions and returning correct value
    non_control_flow_return = [
        '(class dog',
        '# Case 1 - Test a single, constant string return value',
        '(method get_sound ()',
        '(begin',
        '(return "Woof!")',
        '(print "get_sound - I should never be printed")',
        ')',
        ')',
        '# Case 2 - Test simple mathematical expression',
        '(method get_dog_age_multiplier () # Constant 7',
        '(begin',
        '(return (+ 5 2))',
        '(print "get_dog_age_multiplier - I should never be printed")',
        ')',
        ')',
        '# Case 3 - Expression evaluation within a return',
        '(method get_dog_age (human_age)',
        '(begin',
        '(return (* (call me get_dog_age_multiplier) human_age))',
        '(print "get_dog_age - I should never be printed")',
        ')',
        ')',
        '# Case 4 - Expression evaluation with',
        '(method speak ()',
        '(begin',
        '(print (call me get_sound))',
        '(return)',
        '(print "speak - I should never be printed")',
        ')',
        ')',
        ')',
        '(class main',
        '(field puppy_ref null)',
        '(method main ()',
        '(begin',
        '(set puppy_ref (new dog))',
        # '(print "Dog says " (call puppy_ref get_sound))',
        '(print "Dog says his age is: " (call puppy_ref get_dog_age 10))',
        # '(print "Dog spoke! (expect None) - " (call puppy_ref speak))',
        ')',
        ')',
        ')'
    ]
    # Expected output:
    # Dog says Woof!
    # Dog says 70
    # Woof!
    # Dog speaks: (expect None) - None

    # Check that we can instantiate a new object and call its methods
    test_set_instantiation = [
        '(class main',
        '(field other null)',
        '(method main ()',
        '(begin',
        '(set other (new other_class))',  # HERE
        '(call other foo 5 6))))',

        '(class other_class',
        '(field a 10)',
        '(method foo (q r) (print (+ a (+ q r)))))',
    ]

    # Test inline instantation
    test_inline_instantiation = [
        '(class main',
        '(method main ()',
        '(call (new other_class) foo 5 6)',
        ')',
        ')',
        '(class other_class',
        '(field a 10)',
        '(method foo (q r) (print (+ a (+ q r))))',
        ')'
    ]

    # Test return instantiation - return will return a new object of puppy
    test_return_instantiation = [
        '(class main',
        '(field puppy_ref null)',
        '(method main ()',
        '(begin',
        '(print "Adopting a puppy!")',
        '(set puppy_ref (call me adopt_puppy))',
        '(print (call puppy_ref say_thanks))',
        ')',
        ')',
        '(method adopt_puppy()',
        '(return (new puppy))',
        ')',
        ')',
        '(class puppy',
        '(method say_thanks ()',
        '(return "Thank you for adopting me!")',
        ')',
        ')'
    ]

    # Test null return instantiation - return statemenet is empty
    # Should catch and handle this error
    test_null_return_instantiation = [
        '(class main',
        '(field puppy_ref null)',
        '(method main ()',
        '(begin',
        '(print "Adopting two puppies...")',
        '(set puppy_ref (call me adopt_puppy))',
        '(print "No puppies to adopt!")',
        ')',
        ')',
        '(method adopt_puppy()',
        '(return) # Note: this is null',
        ')',
        ')',
        '(class puppy',
        '(method say_thanks ()',
        '(return "Thank you for adopting me!")',
        ')',
        ')'
    ]

    return {'simple': simple, 'many_fields': many_fields, 'simple_begin_test': simple_begin_test, 'nested_begin_test': nested_begin_test, 'set_fields': set_fields,
            'basic_other_call_test': basic_other_call_test, 'basic_self_call_test': basic_self_call_test, 'parameter_other_call_test': parameter_other_call_test,
            'integer_comparison': integer_comparison, 'boolean_comparison': boolean_comparison, 'string_comparison': string_comparison, 'null_comparison': null_comparison,
             'parameter_scoping_test': parameter_scoping_test, 'if_statement': if_statement, 'if_else_statement': if_else_statement, 'while_statement_false': while_statement_false,
             'while_statement_return': while_statement_return, 'non_control_flow_return': non_control_flow_return,'test_set_instantiation': test_set_instantiation,
             'test_inline_instantiation': test_inline_instantiation, 'test_return_instantiation': test_return_instantiation, 'test_null_return_instantiation': test_null_return_instantiation
            #'input_int_test': input_int_test, 'input_str_test': input_str_test, }
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
