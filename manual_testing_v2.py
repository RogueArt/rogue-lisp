#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Dict
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from pprint import pprint


# DEBUGGING ONLY - PLEASE DO NOT PUSH:

def get_test_programs():
    # Legacy test - Verify that program with field types can be parsed (legacy)
    field_types = [
  '(class person',
  '(method nothing ()',
  '(return "")',
  ')',
  ')',
  '(class main',
  '(field int x 10)',
  '(field string y "xyz")',
  '(field person p null)',
  '(method main ()',
  '(print x " " y)',
  ')',
  ')'
]


    return {
        "field_types": field_types,
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
