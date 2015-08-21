#!/usr/bin/env python
__author__ = 'sudipta'

from os import path
from unittest import TestLoader, runner, TestCase, main as unittest_main
from application import task1, task2
from utils import find_closest_factual_id, get_current_device_location_by_ip, get_restaurants


class Task1(TestCase):
    def test_something(self):
        self.assertEqual(True, False)


class Task2(TestCase):
    def test_something(self):
        self.assertEqual(True, False)


class TestUtils(TestCase):
    def test_something(self):
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest_main()
    # loader = TestLoader()
    # tests = loader.discover(start_dir=path.dirname(path.dirname(__file__)))
    #
    # testRunner = runner.TextTestRunner()
    # testRunner.run(tests)



