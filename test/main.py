import unittest

from test_compiler import TestCompiler
from test_global_helpers import TestGlobalHelpers
from test_lexical_analyzer import TestLexicalAnalyzer
from test_op_code import TestOpCodeClass

if __name__ == "__main__":
    test_classes_to_run = [TestCompiler, TestGlobalHelpers, TestLexicalAnalyzer, TestOpCodeClass]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
