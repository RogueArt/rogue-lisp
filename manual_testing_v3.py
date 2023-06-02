#!/usr/bin/python
def get_test_programs():
    # Default value test
    default_value_test = "hello world"

    return {
        "default_value_test": default_value_test.split("\n"),
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