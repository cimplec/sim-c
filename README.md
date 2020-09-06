
# sim-C

<p align="center">
  <img src="./logo.png" height="200">
</p>

[![GitHub](https://img.shields.io/github/license/cimplec/sim-c)](https://github.com/cimplec/sim-c/blob/master/LICENSE)  ![GitHub stars](https://img.shields.io/github/stars/cimplec/sim-c?style=plastic)  ![GitHub contributors](https://img.shields.io/github/contributors/cimplec/sim-c)  ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)  ![GitHub last commit](https://img.shields.io/github/last-commit/cimplec/sim-c)

## What is sim-C?

<p align="justify">Often people have trouble programming in C (especially beginners) due to its low level syntax and unavailability of stable third party libraries. We present sim-C a high-level front end for C which creates a dynamically typed syntax for C. User can write code in this high level syntax and then compile it to optimized C code. sim-C does not process the code and simply translates it to C thus, there is no possibility of the code running slowly. So, with sim-C users can write code faster using the high level syntax and at the same time be able to harness the power and speed of a C program. Let us make C cool again.</p>

## Pipeline

<p align="center">
  <img src="./simc-pipeline.png">
</p>

## Start Contributing

sim-C which has a highly intuitive codebase, you'll be ready to contribute in no time!
While adding any functionality to sim-C you need to make changes in the following files only:

1. **lexical_analyzer.py**
Lexical analysis is the first phase of a compiler. It takes the modified source code from language preprocessors that are written in the form of sentences. The lexical analyzer breaks these syntaxes into a series of tokens, by removing any whitespace or comments in the source code. Depending on the type of functionality add it to the respective function: is_keyword, numeric_val, string_val, keyword_identifier and/or lexical_analyze.

2. **op_code.py**
It is responsible for creating opcodes. If need be you need to change the opcode2dig function only which returns the integer representation of opcode type.

3. **token_class.py**
It is responsible for creating tokens. Here you need to append the token type and its integer reprsentation in the token2dig function.

4. **symbol_table.py**
SymbolTable is responsible for storing information about identifiers and constants.

5. **simc_parser.py**
Parser is an interpreter component that is used to break the data into smaller elements coming from lexical analysis phase. A parser takes input in the form of sequence of tokens and produces output. Here you may need to create a separate function which defines the grammar and checks for the syntax. The function should return the OpCode. Also, if need be you have to append the functionality to the parse function which parses the tokens, calls the particular function and returns opcodes. 

6. **compiler.py**
Finally you need to define the opcode type in the compiler and write the expected C syntax for the functonality.

You can write a test in test.simc and verify whether it's producing results in the test.c file.


## Get started

To get started with simC follow the official documentation:- https://cimplec.github.io/docs/

The following resources are a good place to get to know more about simC:-

1) Writing code in C? Simplify your life with sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj">Dev.to</a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8">Medium</a>.
2) Getting Started with sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek">Dev.to</a>, <a href="https://medium.com/oss-build/getting-started-with-sim-c-1397ee539877">Medium</a>.

Apart from these blog posts, you can also checkout the <a href="https://cimplec.github.io/docs">official docs</a>.

Before moving further please go through the rules in [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

sim-C is licensed under GNU General Public License (GPL) v3.0. [LICENSE](./LICENSE)
