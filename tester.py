"""
Implements all CS 131-related test logic; is entry-point for testing framework.
"""

import asyncio
import importlib
from os import environ
import os
import sys
import traceback
from operator import itemgetter

from harness import (
    AbstractTestScaffold,
    run_all_tests,
    get_score,
    write_gradescope_output,
)


class TestScaffold(AbstractTestScaffold):
    """Implement scaffold for Brewin' interpreter; load file, validate syntax, run testcase."""

    def __init__(self, interpreter_lib):
        self.interpreter_lib = interpreter_lib

    def setup(self, test_case):
        inputfile, expfile, srcfile = itemgetter("inputfile", "expfile", "srcfile")(
            test_case
        )

        with open(expfile, encoding="utf-8") as handle:
            expected = list(map(lambda x: x.rstrip("\n"), handle.readlines()))

        try:
            with open(inputfile, encoding="utf-8") as handle:
                stdin = list(map(lambda x: x.rstrip("\n"), handle.readlines()))
        except FileNotFoundError:
            stdin = None

        with open(srcfile, encoding="utf-8") as handle:
            program = handle.readlines()

        return {
            "expected": expected,
            "stdin": stdin,
            "program": program,
        }

    def run_test_case(self, test_case, environment):
        expect_failure = itemgetter("expect_failure")(test_case)
        stdin, expected, program = itemgetter("stdin", "expected", "program")(
            environment
        )
        interpreter = self.interpreter_lib.Interpreter(False, stdin, False)
        try:
            interpreter.validate_program(program)
            interpreter.run(program)
        except Exception as exception:  # pylint: disable=broad-except
            if expect_failure:
                error_type, _ = interpreter.get_error_type_and_line()
                received = [f"{error_type}"]
                if received == expected:
                    return 1
                print("\nExpected error:")
                print(expected)
                print("\nReceived error:")
                print(received)

            print("\nException: ")
            print(exception)
            traceback.print_exc()
            return 0

        if expect_failure:
            print("\nExpected error:")
            print(expected)
            print("\nActual output:")
            print(interpreter.get_output())
            return 0

        passed = interpreter.get_output() == expected
        if not passed:
            print("\nExpected output:")
            print(expected)
            print("\nActual output:")
            print(interpreter.get_output())

        return int(passed)


def __generate_test_case_structure(
    cases, directory, category="", expect_failure=False, visible=lambda _: True
):
    return [
        {
            "name": f"{category} | {i}",
            "inputfile": f"{directory}{i}.in",
            "srcfile": f"{directory}{i}.brewin",
            "expfile": f"{directory}{i}.exp",
            "expect_failure": expect_failure,
            "visible": visible(f"test{i}"),
        }
        for i in cases
    ]


def __generate_test_suite(version, successes, failures):
    return __generate_test_case_structure(
        successes,
        f"v{version}/tests/",
        "Correctness",
        False,
    ) + __generate_test_case_structure(
        failures,
        f"v{version}/fails/",
        "Incorrectness",
        True,
    )


def generate_test_suite_v1():
    """wrapper for generate_test_suite for v1"""
    return __generate_test_suite(
        1,
        # insert all CORRECTNESS test cases here
        [],
        # ["test_add", "test_case_pass_2", "test_case_pass_3"],
        # insert all INCORRECTNESS test cases here
        []
    )


pass_tests_v2 = [
    'test_add',
    'test_arithmetic',
    'test_begin1',
    'test_begin2',
    'test_bitwise',
    'test_bool_expr',
    'test_bool_expression',
    'test_call_expression',
    'test_call_object_method',
    'test_call_stack',
    'test_compare_bool',
    'test_compare_int',
    'test_compare_null',
    'test_compare_null2',
    # 'test_compare_objects1',
    'test_compare_objects2',
    'test_compare_objects3',
    # 'test_compare_objects4',
    # 'test_compare_objects5',
    'test_compare_string',
    'test_expression_arg',
    'test_factorial',
    'test_fast',
    'test_fields',
    'test_field_types',
    'test_function_call_same_class',
    'test_fwd_call',
    'test_hello_world',
    'test_if',
    'test_if3',
    'test_if_return',
    # 'test_inher1',
    # 'test_inher10',
    # 'test_inher11',
    # 'test_inher12',
    # 'test_inher2',
    # 'test_inher3',
    # 'test_inher4',
    # 'test_inher5',
    # 'test_inher7',
    # 'test_inher8',
    # 'test_inher9',
    # 'test_inher_me1',
    # 'test_inher_me2',
    # 'test_inher_spec',
    'test_inputi',
    'test_inputs',
    'test_instantiate_and_call1',
    'test_instantiate_and_call2',
    'test_instantiate_and_return1',
    'test_instantiate_and_return2',
    'test_ints',
    'test_int_ops',
    'test_knock_knock',
    'test_let',
    'test_let1',
    'test_let2',
    'test_let3',
    'test_let4',
    'test_let5',
    'test_let_mayhem',
    'test_let_shadowing',
    'test_linked_list',
    'test_local_variable',
    'test_method_field_returns',
    'test_nested_calls',
    'test_nested_class',
    'test_nested_let',
    'test_new1',
    'test_new2',
    'test_new_1',
    'test_new_2',
    'test_nothing',
    'test_null',
    'test_null_equality',
    # 'test_null_obj',
    'test_objref',
    'test_objref2',
    # 'test_overload1',
    'test_param_passing1',
    'test_param_passing2',
    # 'test_param_passing3',
    'test_pass_by_value',
    'test_pass_object_param',
    'test_pass_param_between_objects',
    # 'test_polymorphism1',
    # 'test_polymorphism2',
    # 'test_polymorphism3',
    # 'test_polymorphism4',
    'test_print_bool',
    'test_print_combo',
    'test_print_false',
    'test_print_hello',
    'test_print_int',
    'test_print_string',
    'test_print_true',
    'test_recursion1',
    'test_recursion2',
    'test_recursion_1',
    'test_return',
    'test_return_call1',
    'test_return_call2',
    'test_return_call_1',
    'test_return_call_2',
    'test_return_default1',
    'test_return_default2',
    'test_return_default3',
    'test_return_default4',
    'test_return_default5',
    'test_return_default6',
    'test_return_default7',
    'test_return_exit',
    'test_return_exit1',
    'test_return_exit2',
    'test_return_me1',
    'test_return_me2',
    'test_return_method',
    'test_return_type',
    'test_set',
    'test_set1',
    'test_set2',
    # 'test_set3',
    'test_set4',
    'test_set5',
    'test_set6',
    'test_set_bool_field',
    'test_set_constant',
    'test_set_field',
    'test_set_int_field',
    'test_set_obj_field',
    'test_set_param',
    'test_set_string_field',
    'test_shadow',
    'test_str_ops',
    # 'test_super1',
    # 'test_super2',
    'test_unary_not',
    'test_useless_lets',
    'test_valid_assignment1',
    # 'test_valid_assignment2',
    'test_valid_return1',
    'test_valid_return2',
    # 'test_valid_return3',
    'test_valid_return4',
    'test_valid_return5',
    # 'test_valid_return6',
    'test_valid_return7',
    'test_while1',
    'test_while2'
]
fail_tests_v2 = [
    'test_bad_set',
    'test_call_badargs',
    'test_call_invalid_func',
    'test_duplicate_class',
    'test_duplicate_field',
    'test_duplicate_formal_param',
    'test_duplicate_method',
    'test_dup_class',
    'test_dup_field',
    'test_dup_formal_params',
    'test_dup_method',
    'test_eval_invalid_var',
    'test_hello_world',
    'test_incompat_comparison1',
    'test_incompat_comparison2',
    'test_incompat_comparison3',
    'test_incompat_init_field1',
    'test_incompat_init_field2',
    'test_incompat_init_field3',
    'test_incompat_init_field4',
    'test_incompat_operands1',
    'test_incompat_operands2',
    'test_incompat_operands3',
    'test_incompat_operands4',
    'test_incompat_return1',
    'test_incompat_return2',
    'test_incompat_return3',
    'test_incompat_return4',
    'test_incompat_types2',
    'test_inher1',
    'test_inher2',
    # 'test_inher_spec',
    'test_instantiate_invalid',
    'test_invalid_field',
    'test_invalid_if',
    'test_invalid_inputi',
    'test_invalid_inputs',
    'test_invalid_let',
    'test_invalid_let_scope1',
    'test_invalid_let_scope2',
    'test_invalid_let_scope3',
    'test_invalid_method',
    'test_invalid_number_params',
    'test_invalid_object_method',
    'test_invalid_operator1',
    'test_invalid_operator2',
    'test_invalid_param_passing1',
    'test_invalid_param_passing2',
    # 'test_invalid_param_passing3',
    'test_invalid_set1',
    'test_invalid_set2',
    'test_invalid_set_field1',
    'test_invalid_set_field2',
    'test_invalid_while',
    'test_let',
    'test_let2',
    'test_missing_main_class',
    'test_missing_main_func',
    'test_nested_let',
    'test_no_class',
    'test_no_main',
    'test_no_valid_set',
    'test_null_object',
    'test_null_objref',
    # 'test_polymorphism1',
    # 'test_polymorphism2',
    'test_retme',
    # 'test_return_assign_type',
    # 'test_return_assign_type2',
    # 'test_return_assign_type3',
    'test_return_nothing',
    'test_set_fail',
    'test_set_invalid_var',
    'test_str_ops',
    # 'test_type_mismatch'
]

def generate_test_suite_v2():
    """wrapper for generate_test_suite for v2"""
    # test_files = [
    #     file.split(".")[0]
    #     for file in os.listdir("v2/tests")
    #     if file.split(".")[1] == "brewin"
    # ]
    # fail_files = [
    #     file.split(".")[0]
    #     for file in os.listdir("v2/fails")
    #     if file.split(".")[1] == "brewin"
    # ]
    test_files = pass_tests_v2
    fail_files = fail_tests_v2

    return __generate_test_suite(2, test_files, fail_files)



def generate_test_suite_v3():
    """wrapper for generate_test_suite for v3"""
    return __generate_test_suite(3, [], [])


async def main():
    """main entrypoint: argparses, delegates to test scaffold, suite generator, gradescope output"""
    if not sys.argv:
        raise ValueError("Error: Missing version number argument")
    version = sys.argv[1]
    module_name = f"interpreterv{version}"
    interpreter = importlib.import_module(module_name)

    scaffold = TestScaffold(interpreter)

    match version:
        case "1":
            tests = generate_test_suite_v1()
        case "2":
            tests = generate_test_suite_v2()
        case "3":
            tests = generate_test_suite_v3()
        case _:
            raise ValueError("Unsupported version; expect one of 1,2,3")

    results = await run_all_tests(scaffold, tests)
    total_score = get_score(results) / len(results) * 100.0
    print(f"Total Score: {total_score:9.2f}%")

    # flag that toggles write path for results.json
    write_gradescope_output(results, environ.get("PROD", False))


if __name__ == "__main__":
    asyncio.run(main())
