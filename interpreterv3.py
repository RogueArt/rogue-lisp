from v3_class import ClassDef
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from v3_object import ObjectDef
from v3_type_value import TypeManager
import copy

# need to document that each class has at least one method guaranteed

# Main interpreter class
class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    # run a program, provided in an array of strings, one string per line of source code
    # usese the provided BParser class found in parser.py to parse the program into lists
    def run(self, program):
        status, parsed_program = BParser.parse(program)
        if not status:
            super().error(
                ErrorType.SYNTAX_ERROR, f"Parse error on program: {parsed_program}"
            )
        self.__add_all_class_types_to_type_manager(parsed_program)
        self.__map_class_names_to_class_defs(parsed_program)

        # instantiate main class
        invalid_line_num_of_caller = None
        self.main_object = self.instantiate(
            InterpreterBase.MAIN_CLASS_DEF, invalid_line_num_of_caller
        )

        # call main function in main class; return value is ignored from main
        self.main_object.call_method(
            InterpreterBase.MAIN_FUNC_DEF, [], False, invalid_line_num_of_caller
        )

        # program terminates!

    def is_initializer_str(self, class_name):
        return class_name.split(InterpreterBase.TYPE_CONCAT_CHAR)[0] in self.type_manager.map_template_class_name_to_class_def

    # user passes in the line number of the statement that performed the new command so we can generate an error
    # if the user tries to new an class name that does not exist. This will report the line number of the statement
    # with the new command
    def instantiate(self, class_name, line_num_of_statement):
        if class_name not in self.class_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No class named {class_name} found",
                line_num_of_statement,
            )
        
        # Default - assume it's a regular class
        # Additionally, if template was already used, then it's cached
        class_def = self.class_index[class_name]

        # Check if this is a template class
        # If it contains @, then it's actually an initializer string!
        if self.is_initializer_str(class_name):
            initializer_str = class_name
            class_def = self.create_class_def_from_template(initializer_str)

        obj = ObjectDef(
            self, class_def, None, self.trace_output
        )  # Create an object based on this class definition
        return obj

    # returns a ClassDef object
    def get_class_def(self, class_name, line_number_of_statement):
        if class_name not in self.class_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No class named {class_name} found",
                line_number_of_statement,
            )
        return self.class_index[class_name]

    # returns a bool
    def is_valid_type(self, typename):
        return self.type_manager.is_valid_type(typename)

    # returns a bool
    def is_a_subtype(self, suspected_supertype, suspected_subtype):
        return self.type_manager.is_a_subtype(suspected_supertype, suspected_subtype)

    # typea and typeb are Type objects; returns true if the two type are compatible
    # for assignments typea is the type of the left-hand-side variable, and typeb is the type of the
    # right-hand-side variable, e.g., (set person_obj_ref (new teacher))
    def check_type_compatibility(self, typea, typeb, for_assignment=False):
        return self.type_manager.check_type_compatibility(typea, typeb, for_assignment)

    def __map_class_names_to_class_defs(self, program):
        self.class_index = {}
        for item in program:
            if item[0] == InterpreterBase.CLASS_DEF:
                if item[1] in self.class_index:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Duplicate class name {item[1]}",
                        item[0].line_num,
                    )
                self.class_index[item[1]] = ClassDef(item, self)
            elif item[0] == InterpreterBase.TEMPLATE_CLASS_DEF:
                if item[1] in self.class_index:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Duplicate class name {item[1]}",
                        item[0].line_num,
                    )
                
                # Template class, we need to set parameter types as well
                # 1. Show it's a template with a boolean
                template_class_def = ClassDef(item, self, is_template_class=True)

                # 2. Parse the parameters and put it in the class definition
                template_class_def.set_parameter_type_strings(item[2])

                self.class_index[item[1]] = template_class_def
                self.type_manager.add_template_class_type(item[1], template_class_def)

    # [class classname inherits superclassname [items]]
    def __add_all_class_types_to_type_manager(self, parsed_program):
        self.type_manager = TypeManager()
        for item in parsed_program:
            if item[0] == InterpreterBase.CLASS_DEF:
                class_name = item[1]
                superclass_name = None
                if item[2] == InterpreterBase.INHERITS_DEF:
                    superclass_name = item[3]
                self.type_manager.add_class_type(class_name, superclass_name)
            # Note: we add template class types AFTER provided parameters

    def create_class_def_from_template(self, template_class_initializer):
        # Process this string
        template_class_name, provided_types = self.type_manager.split_template_class_initializer(template_class_initializer)

        # Verify that the class is valid
        if not self.type_manager.is_template_class_initializer_str_valid(template_class_initializer):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Invalid template class initializer: {template_class_initializer}",
                template_class_initializer.line_num, # TO-DO: Will this work?
            )

        # Check if this class has already been initialized
        if template_class_initializer in self.class_index:
            # If so, then we can just return it
            return self.class_index[template_class_initializer]

        template_class_def = self.type_manager.map_template_class_name_to_class_def[template_class_name]

        # Create a deepcopy of this source
        # Mutate this so it looks like a real class
        template_class_source = copy.deepcopy(template_class_def.class_source)
        template_class_source[0] = InterpreterBase.CLASS_DEF
        template_class_source[1] = template_class_initializer
        del template_class_source[2]  # Delete the parameter types

        # Recursively find and replace all parameter types in class_source with provided types
        for x in range(len(provided_types)):
            # Template type = what's in the template class definition already
            template_type = template_class_def.parameter_type_strings[x]
            # Provided type is what the user gave, that we're replacing it with
            provided_type = provided_types[x]
            
            template_class_source = self.type_manager.replace_parameter_strings(template_class_source, template_type, provided_type)

        # Attach this to the type mananger
        # Note: there's no super class for this
        self.type_manager.add_class_type(template_class_initializer, None)

        # Create a new class definition with this new source
        # Note: This class is not a template, so we pass in False
        new_class_def = ClassDef(template_class_source, self)
        self.class_index[template_class_initializer] = new_class_def

        return new_class_def    

# CODE FOR DEBUGGING PURPOSES ONLY
if __name__ == "__main__":
    from manual_testing_v3 import get_test_programs

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

    test_programs = get_test_programs()
    skip_tests = []  # , 'set_fields'
    # skip_tests = ['field_and_method_types']
    run_tests = []
    # run_tests = ['test_set_instantiation', 'test_return_instantiation', 'test_null_return_instantiation'] 
    for count, (program_name, program) in enumerate(test_programs.items()):
        if (len(run_tests) > 0 and program_name not in run_tests) or program_name in skip_tests:
            print(YELLOW + f"Skipping test #{count+1} {program_name}" + RESET)
            continue

        if (len(run_tests) > 0 and program_name in run_tests) or len(run_tests) == 0:
            try:
                print(GREEN + f"Running test #{count+1} {program_name}:" + RESET)
                interpreter = Interpreter()
                interpreter.run(program)
                print(GREEN + f"Finished testing {program_name}\n\n" + RESET)
            except RuntimeError as e:
                if e.args[0] == 'ErrorType.TYPE_ERROR':
                    print("Code exited with ErrorType.TYPE_ERROR")
                elif e.args[0] == 'ErrorType.NAME_ERROR':
                    print("Code exited with ErrorType.NAME_ERROR")
                elif e.args[0] == 'ErrorType.SYNTAX_ERROR':
                    print("Code exited with ErrorType.SYNTAX_ERROR")
                elif e.args[0] == 'ErrorType.FAULT_ERROR':
                    print("Code exited with ErrorType.FAULT_ERROR")
                else:
                    raise e
