from intbase import InterpreterBase, ErrorType


class Interpreter(InterpreterBase):
    def __init__(self, console_ouptput=True, trace_output=False):
        # call InterpreterBase's constructor
        super().__init__(console_ouptput, trace_output)

    def run(self, program):
        Interpreter.output('hello world!')


program = ['(class main',
           '(method hello_world () (print “hello world!”))',
           ')']

interpreter = Interpreter()
interpreter.run(program)
