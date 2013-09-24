#!/usr/bin/env python
import imp
import os.path
import subprocess
import unittest
from impl.git import GitImpl

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

	def assertDiffTransformation(self, case):
		case_module_path = os.path.join(MY_DIRECTORY, 'cases', case + '.py')
		case_module = imp.load_source('case', case_module_path)

		expected_output_file = os.path.join(MY_DIRECTORY, 'expected', case + '.diff')
		expected_output = load_file(expected_output_file)

		git_impl = GitImpl()
		revs = case_module.run(git_impl)
		if revs:
			revision_args = ['-r', ':'.join(str(rev) for rev in revs)]
		else:
			revision_args = []

		cmd = [COMMAND_PATH, '-v'] + revision_args
		output = subprocess.check_output(cmd, cwd=git_impl.client_path)

		save_file(os.path.join(git_impl.temp_path, 'git-svn.diff'), output)
		save_file(os.path.join(git_impl.temp_path, 'svn.diff'), expected_output)

		self.assertEqual(expected_output, output)

	def testMultipleChanges(self):
		self.assertDiffTransformation('multiple_changes')

	def testFileAdded(self):
		self.assertDiffTransformation('file_added')

	def testFileEmptiedOrRemoved(self):
		self.assertDiffTransformation('file_emptied_or_removed')

	def testOneRevisionParameterR1(self):
		self.assertDiffTransformation('one_revision_parameter_r1')

	def testOneRevisionParameterR2(self):
		self.assertDiffTransformation('one_revision_parameter_r2')

	def testOneRevisionParameterR3(self):
		self.assertDiffTransformation('one_revision_parameter_r3')

	def testTwoRevisionParametersR1R2(self):
		self.assertDiffTransformation('two_revision_parameters_r1_r2')

	def testTwoRevisionParametersR1R3(self):
		self.assertDiffTransformation('two_revision_parameters_r1_r3')

	def testTwoRevisionParametersR2R3(self):
		self.assertDiffTransformation('two_revision_parameters_r2_r3')


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
