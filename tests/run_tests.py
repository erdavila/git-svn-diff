#!/usr/bin/env python
from __future__ import print_function
import os.path
import subprocess
import unittest
from impl.git import GitImpl
import cases.multiple_changes
import cases.file_added

MY_DIRECTORY, _ = os.path.split(__file__)
COMMAND_PATH = os.path.abspath(os.path.join(MY_DIRECTORY, '..', 'git_svn_diff.py'))

def load_file(filename):
	with open(filename) as f:
		return f.read()

def save_file(filename, content):
	with open(filename, 'w') as f:
		f.write(content)


class Test(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def assertDiffTransformation(self, case_module, expected_output_file):
		expected_output_file = os.path.join(MY_DIRECTORY, 'expected', expected_output_file + '.diff')
		expected_output = load_file(expected_output_file)

		git_impl = GitImpl()
		case_module.run(git_impl)

		output = subprocess.check_output([COMMAND_PATH], cwd=git_impl.client_path)

		save_file(os.path.join(git_impl.temp_path, 'git-svn-diff.output'), output)
		save_file(os.path.join(git_impl.temp_path, 'svn-diff.output'), expected_output)

		self.assertEqual(expected_output, output)

	def testMultipleChanges(self):
		expected_output_file = 'multiple_changes'
		self.assertDiffTransformation(cases.multiple_changes, expected_output_file)

	def testFileAdded(self):
		expected_output_file = 'file_added'
		self.assertDiffTransformation(cases.file_added, expected_output_file)


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
