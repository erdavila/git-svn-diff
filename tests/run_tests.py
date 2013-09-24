#!/usr/bin/env python
import imp
import os.path
import subprocess
import unittest
from impl.git import GitImpl

MY_DIRECTORY, _ = os.path.split(__file__)
COMMAND_PATH = os.path.abspath(os.path.join(MY_DIRECTORY, '..', 'git_svn_diff.py'))
git_svn_diff = imp.load_source('git_svn_diff', COMMAND_PATH)

def load_file(filename):
	with open(filename) as f:
		return f.read()

def save_file(filename, content):
	with open(filename, 'w') as f:
		f.write(content)


class DiffTransformationTest(unittest.TestCase):

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


class ArgumentsParserTest(unittest.TestCase):
	
	def setUp(self):
		self.parser = git_svn_diff.ArgumentsParser()

	def testNoArgs(self):
		version1, version2, verbose = self.parser.parse([])
		self.assertVersion(version1, commit=None, rev=None, arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testRevisionArg1(self):
		version1, version2, verbose = self.parser.parse(['r123'])
		self.assertVersion(version1, commit=None, rev=123,  arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testRevisionArg2(self):
		version1, version2, verbose = self.parser.parse(['-r', '123'])
		self.assertVersion(version1, commit=None, rev=123,  arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testCommitArg(self):
		version1, version2, verbose = self.parser.parse(['deadbeef'])
		self.assertVersion(version1, commit='deadbeef', rev=None, arev=None)
		self.assertVersion(version2, commit=None,       rev=None, arev=None)
		self.assertFalse(verbose)

	def testCommitAndAssumedRevisionArg1(self):
		version1, version2, verbose = self.parser.parse(['deadbeef', '--assume-rev1=123'])
		self.assertVersion(version1, commit='deadbeef', rev=None, arev=123)
		self.assertVersion(version2, commit=None,       rev=None, arev=None)
		self.assertFalse(verbose)

	def testCommitAndAssumedRevisionArg2(self):
		version1, version2, verbose = self.parser.parse(['--assume-rev1=123', 'deadbeef'])
		self.assertVersion(version1, commit='deadbeef', rev=None, arev=123)
		self.assertVersion(version2, commit=None,       rev=None, arev=None)
		self.assertFalse(verbose)

	def testOnlyAssumedRevision1(self):
		version1, version2, verbose = self.parser.parse(['--assume-rev1=123'])
		self.assertVersion(version1, commit=None, rev=None, arev=123)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testOnlyAssumedRevision2(self):
		version1, version2, verbose = self.parser.parse(['--assume-rev1', '123'])
		self.assertVersion(version1, commit=None, rev=None, arev=123)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testOnlyAssumedRevision3(self):
		version1, version2, verbose = self.parser.parse(['--r1=123'])
		self.assertVersion(version1, commit=None, rev=None, arev=123)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testOnlyAssumedRevision4(self):
		version1, version2, verbose = self.parser.parse(['--r1', '123'])
		self.assertVersion(version1, commit=None, rev=None, arev=123)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertFalse(verbose)

	def testTwoRevisions1(self):
		version1, version2, verbose = self.parser.parse(['r12345', 'r6789'])
		self.assertVersion(version1, commit=None, rev=12345, arev=None)
		self.assertVersion(version2, commit=None, rev=6789,  arev=None)
		self.assertFalse(verbose)

	def testTwoRevisions2(self):
		version1, version2, verbose = self.parser.parse(['-r', '12345', '-r', '6789'])
		self.assertVersion(version1, commit=None, rev=12345, arev=None)
		self.assertVersion(version2, commit=None, rev=6789,  arev=None)
		self.assertFalse(verbose)

	def testTwoRevisionsAsInterval(self):
		version1, version2, verbose = self.parser.parse(['-r', '12345:6789'])
		self.assertVersion(version1, commit=None, rev=12345, arev=None)
		self.assertVersion(version2, commit=None, rev=6789,  arev=None)
		self.assertFalse(verbose)

	def testTwoCommits(self):
		version1, version2, verbose = self.parser.parse(['dead', 'beef'])
		self.assertVersion(version1, commit='dead', rev=None, arev=None)
		self.assertVersion(version2, commit='beef', rev=None,  arev=None)
		self.assertFalse(verbose)

	def testAssumedRevisionForSecondCommit1(self):
		version1, version2, verbose = self.parser.parse(['--assume-rev2=666'])
		self.assertVersion(version1, commit=None, rev=None, arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=666)
		self.assertFalse(verbose)

	def testAssumedRevisionForSecondCommit2(self):
		version1, version2, verbose = self.parser.parse(['--assume-rev2', '666'])
		self.assertVersion(version1, commit=None, rev=None, arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=666)
		self.assertFalse(verbose)

	def testAssumedRevisionForSecondCommit3(self):
		version1, version2, verbose = self.parser.parse(['--r2=666'])
		self.assertVersion(version1, commit=None, rev=None, arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=666)
		self.assertFalse(verbose)

	def testAssumedRevisionForSecondCommit4(self):
		version1, version2, verbose = self.parser.parse(['--r2', '666'])
		self.assertVersion(version1, commit=None, rev=None, arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=666)
		self.assertFalse(verbose)

	def testTooManyArgs1(self):
		f = lambda: self.parser.parse(['deadbeef', 'r123', 'abcdef'])
		self.assertRaises(Exception, f)

	def testTooManyArgs2(self):
		f = lambda: self.parser.parse(['deadbeef', 'r123', 'r456789'])
		self.assertRaises(Exception, f)

	def testTooManyArgs3(self):
		f = lambda: self.parser.parse(['deadbeef', '-r', '123', '-r', '456789'])
		self.assertRaises(Exception, f)

	def testTooManyArgs4(self):
		f = lambda: self.parser.parse(['deadbeef', '-r', '12345:6789'])
		self.assertRaises(Exception, f)

	def testTooManyArgs5(self):
		f = lambda: self.parser.parse(['-r', '12345:6789', 'deadbeef'])
		self.assertRaises(Exception, f)

	def testTooManyArgs6(self):
		f = lambda: self.parser.parse(['-r', '123:456', 'r789'])
		self.assertRaises(Exception, f)

	def testRevisionWithAssumedRevision(self):
		f = lambda: self.parser.parse(['r123', '--assume-rev1=456'])
		self.assertRaises(Exception, f)

	def testAssumedRevisionTwice(self):
		f = lambda: self.parser.parse(['--assume-rev1=12345', '--assume-rev1=6789'])
		self.assertRaises(Exception, f)

	def testVerbose(self):
		version1, version2, verbose = self.parser.parse(['-v'])
		self.assertVersion(version1, commit=None, rev=None, arev=None)
		self.assertVersion(version2, commit=None, rev=None, arev=None)
		self.assertTrue(verbose)

	def testComplete(self):
		version1, version2, verbose = self.parser.parse(['deadbeef', 'r123', '-v', '--assume-rev1', '666'])
		self.assertVersion(version1, commit='deadbeef', rev=None, arev=666)
		self.assertVersion(version2, commit=None,       rev=123,  arev=None)
		self.assertTrue(verbose)

	def assertVersion(self, version, commit, rev, arev):
		self.assertEqual(commit, version.commit)
		self.assertEqual(rev, version.revision)
		self.assertEqual(arev, version.assumed_revision)


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
