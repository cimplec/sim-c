# Contributing to simC   

### Please star (⭐) the repository to show your support to the project.    

## Pull Requests (PRs)

- PR will be reviewed within a maximum of 72 hours of submitting the request.
- The following rules are to be followed while submitting a PR:-
	- <strong>Branch Name</strong>: The name of the branch should start with 'in' followed by hyphen (-) and the issue number. Eg:- If you are working on issue number 57 then your branch name should be in-57. You need to make sure that in your fork you create a branch following this pattern.
	- <strong>Commit Message</strong>: Commit message should make sense, anyone should be able to get an idea of what changes were made in that particular commit. Irrelevant or inapporpriate commit messages are highly discouraged.
	- <strong>Docstrings</strong>: Docstrings are special comments in python which helps one to understand what a function or class does, the parameters passed, and the data returned from that function. We tend to follow a similar syntax for javascript too, we expect everyone to adhere to the format in your code. To get a better idea of the format of docstrings, please refer to the codebase.
	- <strong>Comments</strong>: The comments should be meaningful and one should be able to understand what the line(s) of code mean from the comments. Do not add unecessary comments in each line, leave out comments from code which is self-explanatory. 
	- <strong>Variables</strong>: Variable names used in your code should explain what the variable is. Some unacceptable variable names are:- a, b, hello, world, etc.  While creating variable name with multiple words in it, the words should be separated by underscore (_) e.g:- player_initial_energy and should not be written in camel case e.g- playerInitialEnergy.
	- <strong>Run tests</strong>: Run the tests using simC's test-suite and report the number of tests passing, if this is missing then the PR will be closed immediately.
	- <strong>Follow PR template</strong>: Fill all the details in PR template as it helps us understand the PR better, the PR will be closed if any field is found empty.
- After successful submission of PR, it will be subjected to automated testing and if the code fails any of the tests you will be given a time period of 3 days to fix the issue, else your PR will be closed.

## New Issue (New feature or bug)

- The time period for reviewing of a new issue is a maximum of 36 hours, you can expect to hear from a maintainer within this time frame.
- The implementation of the new feature or fixing of the bug should only be started after a maintainer approves the feature or bug report in the discussion. 
- Once approved start implementing the feature or fix the bug and submit a pull request.

## Start Contributing

<p align="justify">Go through <a href="https://github.com/cimplec/sim-c/wiki/">simC's Wiki</a> to get an in-depth understanding of simC.</p>

<p align="justify">Three files are important and if you are contributing to this project, you should have a rough idea of these files, the order is:-</p>

- [lexical_analyzer.py](./simc/lexical_analyzer.py)
- [simc_parser.py](./simc/parser/simc_parser.py)
- [compiler.py](./simc/compiler.py)


## Contributing
<span id="contribute"></span>
To get started with simC follow the official documentation:- https://cimplec.github.io/docs/

The following resources are a good place to get to know more about simC:-

1) Writing code in C? Simplify your life with sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj">Dev.to</a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8">Medium</a>.
2) Getting Started with sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek">Dev.to</a>, <a href="https://medium.com/oss-build/getting-started-with-sim-c-1397ee539877">Medium</a>.

Apart from these blog posts, you can also checkout the <a href="https://cimplec.github.io/docs">official docs</a>.  

## Unit Testing

- Make sure you test your code using the test suite before you make a PR. 
- To test your code, the steps are as follows:-
	1) Install sim-C test suite:-
	```bash
	user@programm~:$ pip install git+https://github.com/cimplec/test-suite
	```
	2) Run the tests
	```bash
	user@programmer~:$ simc-test
	```
- If any test fails make sure to fix your code so that the error goes away. 

