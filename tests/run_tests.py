#!/usr/bin/env python
import imp
import os.path
import re
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

	def assertDiffTransformation(self, case, convert_revision_to_commit=False, arguments=None, expected=None):
		case_module_path = os.path.join(MY_DIRECTORY, 'cases', case + '.py')
		case_module = imp.load_source('case', case_module_path)

		if expected is None:
			expected = case
		expected_output_file = os.path.join(MY_DIRECTORY, 'expected', expected + '.diff')
		expected_output = load_file(expected_output_file)

		git_impl = GitImpl()
		revisions = case_module.run(git_impl)
		if arguments is None:
			if revisions:
				if convert_revision_to_commit:
					arguments = []
					for rev in revisions:
						commit = subprocess.check_output(['git', 'svn', 'find-rev', 'r%d' % rev], cwd=git_impl.client_path)
						commit = commit.strip()
						arguments.append(commit)
				else:
					arguments = ['-r', ':'.join(str(rev) for rev in revisions)]
			else:
				arguments = []

		cmd = [COMMAND_PATH, '-v'] + arguments
		print "Executing %r" % cmd
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
	
	def testNonSHA1CommitParameter(self):
		self.assertDiffTransformation('one_revision_parameter_r1', arguments=['HEAD~2'])
	
	def testOneCommitParameterR1(self):
		self.assertDiffTransformation('one_revision_parameter_r1', convert_revision_to_commit=True)
	
	def testOneCommitParameterR2(self):
		self.assertDiffTransformation('one_revision_parameter_r2', convert_revision_to_commit=True)
	
	def testOneCommitParameterR3(self):
		self.assertDiffTransformation('one_revision_parameter_r3', convert_revision_to_commit=True)
	
	def testTwoCommitParametersR1R2(self):
		self.assertDiffTransformation('two_revision_parameters_r1_r2', convert_revision_to_commit=True)
	
	def testTwoCommitParametersR1R3(self):
		self.assertDiffTransformation('two_revision_parameters_r1_r3', convert_revision_to_commit=True)
	
	def testTwoCommitParametersR2R3(self):
		self.assertDiffTransformation('two_revision_parameters_r2_r3', convert_revision_to_commit=True)
	
	def testCommitAndRevisionParametersR1R3(self):
		self.assertDiffTransformation('two_revision_parameters_r1_r3', arguments=['HEAD~2', 'HEAD'])
	
	def testCommitsWithAssumedRevisions(self):
		arguments = [
			'HEAD~1', '--r1=666',
			'HEAD', '--assume-rev2', '1024',
		]
		self.assertDiffTransformation('two_revision_parameters_r2_r3',
				arguments=arguments,
				expected='commits_with_assumed_revisions'
		)


class PipeDiffTransformationTest(unittest.TestCase):
	
	def assertDiffTransformation(self, case):
		case_module_path = os.path.join(MY_DIRECTORY, 'cases', case + '.py')
		case_module = imp.load_source('case', case_module_path)

		expected = case
		expected_output_file = os.path.join(MY_DIRECTORY, 'expected', expected + '.diff')
		expected_output = load_file(expected_output_file)

		git_impl = GitImpl()
		revisions = case_module.run(git_impl)
		commits = []
		assumed_revisions = []
		if revisions:
			for rev in revisions:
				commit = subprocess.check_output(['git', 'svn', 'find-rev', 'r%d' % rev], cwd=git_impl.client_path)
				commit = commit.strip()
				
				commits.append(commit)
				assumed_revisions.append(rev)
		else:
			commit = 'HEAD'
			revision = subprocess.check_output(['git', 'svn', 'find-rev', commit], cwd=git_impl.client_path)
			commits.append(commit)
			assumed_revisions.append(int(revision))
		
		git_diff_cmd = 'git diff %s' % ' '.join(commits)
		git_svn_diff_cmd = '%s -v %s' % (COMMAND_PATH, ' '.join('--r%d=%d' % (n, rev) for n, rev in enumerate(assumed_revisions, 1)))
		cmd = git_diff_cmd + ' | ' + git_svn_diff_cmd
		print "Executing %r" % cmd
		output = subprocess.check_output(cmd, shell=True, cwd=git_impl.client_path)

		save_file(os.path.join(git_impl.temp_path, 'git-svn.diff'), output)
		save_file(os.path.join(git_impl.temp_path, 'svn.diff'), expected_output)

		self.assertEqual(expected_output, output)

	def testMultipleChanges(self):
		self.assertDiffTransformation('multiple_changes')
	
	def testOneRevisionParameterR1(self):
		self.assertDiffTransformation('one_revision_parameter_r1')
	
	def testTwoRevisionParametersR1R3(self):
		self.assertDiffTransformation('two_revision_parameters_r1_r3')


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


class VersionsSolverTest(unittest.TestCase):
	
	def setUp(self):
		self.version1 = git_svn_diff.Version()
		self.version2 = git_svn_diff.Version()
		self.git_impl = GitImpl()
		self.solver = git_svn_diff.VersionsSolver(cwd=self.git_impl.client_path)
	
	def testVersion1Default(self):
		self.solver.solve_version1(self.version1)
		
		self.assertSolvedVersion(self.version1, commit='HEAD', arev=1)
	
	def testVersion1AsCommit(self):
		EXPECTED_COMMIT = self.getCurrentCommit()
		EXPECTED_REVISION = self.getCurrentRevision()
		self.version1.commit = EXPECTED_COMMIT
		
		self.solver.solve_version1(self.version1)
		
		self.assertSolvedVersion(self.version1, commit=EXPECTED_COMMIT, arev=EXPECTED_REVISION)

	def testVersion1AsCommitWithAssumedRevision(self):
		EXPECTED_COMMIT = 'deadbeef'
		EXPECTED_REVISION = 321
		self.version1.commit = EXPECTED_COMMIT
		self.version1.assumed_revision = EXPECTED_REVISION
		
		self.solver.solve_version1(self.version1)
		
		self.assertSolvedVersion(self.version1, commit=EXPECTED_COMMIT, arev=EXPECTED_REVISION)

	def testVersion1AsRevision(self):
		EXPECTED_COMMIT = self.getCurrentCommit()
		EXPECTED_REVISION = self.getCurrentRevision()
		self.version1.revision = EXPECTED_REVISION
		
		self.solver.solve_version1(self.version1)
		
		self.assertSolvedVersion(self.version1, commit=EXPECTED_COMMIT, arev=EXPECTED_REVISION)
	
	def testVersion2Default(self):
		self.solver.solve_version2(self.version2)
		
		self.assertSolvedVersion(self.version2, commit=None,   arev=None)
	
	def testVersion2AsCommit(self):
		EXPECTED_COMMIT = self.getCurrentCommit()
		self.version2.commit = EXPECTED_COMMIT
		
		self.solver.solve_version2(self.version2)
		
		self.assertSolvedVersion(self.version2, commit=EXPECTED_COMMIT, arev=1)
	
	def testVersion2AsCommitWithAssumedRevision(self):
		EXPECTED_COMMIT = self.getCurrentCommit()
		EXPECTED_REVISION = 456
		self.version2.commit = EXPECTED_COMMIT
		self.version2.assumed_revision = EXPECTED_REVISION
		
		self.solver.solve_version2(self.version2)
		
		self.assertSolvedVersion(self.version2, commit=EXPECTED_COMMIT, arev=EXPECTED_REVISION)

	def testVersion2AsRevision(self):
		EXPECTED_COMMIT = self.getCurrentCommit()
		EXPECTED_REVISION = self.getCurrentRevision()
		self.version2.revision = EXPECTED_REVISION
		
		self.solver.solve_version2(self.version2)
		
		self.assertSolvedVersion(self.version2, commit=EXPECTED_COMMIT, arev=EXPECTED_REVISION)
	
	def getCurrentCommit(self):
		commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.git_impl.client_path)
		commit = commit.strip()
		return commit
	
	def getCurrentRevision(self):
		output = subprocess.check_output(['git', 'svn', 'info'], cwd=self.git_impl.client_path)
		m = re.search(r'\nRevision: (\d+)\n', output)
		revision = int(m.group(1))
		return revision

	def assertSolvedVersion(self, version, commit, arev):
		self.assertEqual(commit, version.commit)
		self.assertEqual(arev, version.assumed_revision)


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
