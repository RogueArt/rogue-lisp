# RogueLisp: Minimalist Lisp Interpreter in Python

RogueLisp is a fully functional Lisp interpreter built from scratch in Python. Designed for extensibility and clarity, RogueLisp leverages modern object-oriented design patterns to support key language features and make future expansion easy.

## ✨ Features

- **Recursive descent parser** for S-expressions, arithmetic, variables, functions, and control flow
- **Object-oriented architecture:** Each Lisp form and built-in function is represented by a class, using inheritance and polymorphism for dynamic dispatch and clean extensibility
- **Nested scope management** and first-class functions
- **Robust error handling** for syntax errors, undefined variables, and arity mismatches
- **Test-driven development:** Comprehensive unit and integration tests for parser, evaluator, and spec compliance

## 🛠️ Technical Highlights

- Modularized Lexer and Parser for clear separation of concerns
- Evaluator engine refactored into polymorphic, extensible instruction classes
- New language constructs can be added by subclassing core AST and evaluation classes
- Extensive code documentation and examples for users and contributors

## 📈 Skills Demonstrated

- Interpreter/compiler construction
- Advanced Python: OOP, inheritance, polymorphism, and modular design
- Functional programming and recursion
- Test-driven development and compliance testing
- Software architecture and extensibility

### 🚀 Sample Usage

```lisp
(class person 
  (field string name "jane")
  (method void set_name((string n)) (set name n))
  (method string get_name() (return name))
)

(class student inherits person
  (field int beers 3)
  (field string student_name "studentname")
  (method void set_beers((int g)) (set beers g))
  (method int get_beers() (return beers))
  (method string get_name() (return student_name))
)

(class main
  (field student s null)
  (method void main () 
    (begin 
      (set s (new student))
      (print (call s get_name))
    )
  )
)

# Output:
# "jane"
```

## 📚 Project Motivation

RogueLisp was built to deeply explore interpreter design, functional programming, and language architecture. All parsing, evaluation, environment, and OOP logic were engineered from scratch, with extensibility and clean design as guiding principles.

## 📦 Repository

See [pull requests](https://github.com/RogueArt/rogue-lisp/pulls?q=is%3Apr+is%3Aclosed) for implementation milestones and new feature expansions.
