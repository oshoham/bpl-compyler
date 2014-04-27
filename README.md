bpl
===

A compiler for Bob's Programming Language, a simple, C-like language. Implemented for the Spring 2014 CS331 course at Oberlin College.

Written in Python 2.7.6. Compiles to GAS instructions.

### Structure

The compiler consists of 4 modules: 
    1. a lexical scanner that tokenizes text files
    2. a recursive descent parser that constructs abstract syntax trees from token streams
    3. a type checker that traverses abstract syntax trees to catch type errors
    4. a code generator that converts type-correct ASTs to GNU AS instructions.

The code is organized as follows:

    .                           # top-level directory.  Run tests from here!
    ├── README.md
    └── bpl                     # bpl python package
        ├── __init__.py
        ├── __main__.py         # main module for bpl package
        |
        ├── scanner             # scanner package
        │   ├── __init__.py
        │   ├── scanner.py
        │   ├── token.py
        |
        |── parser              # parser package
        │   ├── __init__.py
        |   |── parser.py
        |   |── parsetree.py
        |
        |── type_checker        # type checker package
        │   ├── __init__.py
        |   |── type_checker.py
        |
        |── code_generator      # code generator package
        │   ├── __init__.py
        |   |── code_generator.py
        |
        └── test                # test package
            ├── __init__.py
            ├── example.bpl
            ├── scanner_test.py
            ├── parser_test.py
            ├── type_checker_test.py
            └── code_generator_test.py

(credit to [@daf-](https://github.com/daf-/) for this diagram and the structure of this README)

### Running the Compiler

To run the compiler, run the `bplc` script from the top-level directory as follows:

```
$ ./bplc <filename>
```

### Tests

To test a module `foo`, run the following command from the top-level directory:

```
$ python -m bpl.test.foo_test <filename>
```
