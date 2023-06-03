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

def generate_test_suite_v2():
    """wrapper for generate_test_suite for v2"""
    test_files = [
        file.split(".")[0]
        for file in os.listdir("v2/tests")
        if file.split(".")[1] == "brewin"
    ]
    fail_files = [
        file.split(".")[0]
        for file in os.listdir("v2/fails")
        if file.split(".")[1] == "brewin"
    ]

    return __generate_test_suite(2, test_files, fail_files)

test_files = [
    "test_default_fields",
    "test_default_locals",
    "test_except1",
    "test_except13",
    "pisk_except_in_catch",
    "pisk_nested_try",
    "test_str_ops",
    "pisk_template_class_only",
    "test_template",
    "test_template1",
    "test_template2",
    "test_template3",
    "test_template4",
    "test_template8",
    "test_template9",
    "test_template_test",
    "test_throw",
    "test_throw2",
    "test_throw3",
    "test_throw4",
    "test_throw5",
    "test_try",
    "test_try1"
]

fail_files = [
    "pisk_test_except1",
    "pisk_test_except2",
    "test_except4",
    "test_incompat_template_types",
    "test_template10",
    "test_template11",
    "test_template5",
    "test_template6",
    "test_template7",
    "test_template8",
    "test_template9"
]


def generate_test_suite_v3():
    """wrapper for generate_test_suite for v3"""
    return __generate_test_suite(3, test_files, fail_files)


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
