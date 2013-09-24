#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess


class DiffTransformer(object):

	def __init__(self, revision1, revision2):
		self.revision1 = revision1
		self.revision2 = revision2

	def transform_line(self, line):
		if line.startswith('diff --git '):
			m = re.search(r'^diff --git (.+) \1$', line)
			self.filename = m.group(1)
			return 'Index: ' + self.filename
		elif line.startswith('index '):
			return 67 * '='
		elif line.startswith('--- '):
			if line == '--- /dev/null':
				rev = 0
			else:
				rev = self.revision1
			return '--- %s\t(revision %d)' % (self.filename, rev)
		elif line.startswith('+++ '):
			if self.revision2 is None:
				rev_str = 'working copy'
			else:
				rev_str = 'revision %d' % self.revision2
			return '+++ %s\t(%s)' % (self.filename, rev_str)
		elif line.startswith('new file mode ') or line.startswith('deleted file mode '):
			return None
		else:
			return line


def main():
	revision1, revision2, verbose = process_arguments()
	if revision1 is None:
		assert revision2 is None, revision2
		commits = ['HEAD']
		revision1 =  commit_to_revision('HEAD')
	else:
		commits = [revision_to_commit(revision1)]
		if revision2 is not None:
			commits.append(revision_to_commit(revision2))

	cmd = ['git', 'diff', '--no-prefix'] + commits
	if verbose:
		import sys
		print('Executing %r' % cmd, file=sys.stderr)
	output = subprocess.check_output(cmd)

	lines = output.splitlines()
	transformer = DiffTransformer(revision1, revision2)
	for line in lines:
		line = transformer.transform_line(line)
		if line is not None:
			print(line)


class Version(object):
	def __init__(self, commit=None, revision=None, assumed_revision=None):
		self.commit = commit
		self.revision = revision
		self.assumed_revision = assumed_revision


class ArgumentsParser(object):
	
	def __init__(self):
		self._versions = None
		self._arguments = None
	
	def parse(self, arguments):
		self._versions = Version(), Version()
		self._arguments = list(arguments)
		
		verbose = False
	
		while self._arguments:
			arg = self._arguments.pop(0)
			if arg == '-r':
				arg = self._next_argument()
				if re.match(r'\d+:\d+$', arg):
					if self._is_defined(self._versions[0]):
						raise Exception("Too many _arguments")
					revision0, revision1 = arg.split(':')
					self._versions[0].revision = int(revision0)
					self._versions[1].revision = int(revision1)
				else:
					revision = int(arg)
					self._set_revision(revision)
			elif re.match(r'r\d+$', arg):
				revision = int(arg[1:])
				self._set_revision(revision)
			elif re.match(r'[0-9a-f]{4,40}$', arg, re.IGNORECASE):
				self._set_commit(arg)
			elif arg == '--assume-rev1':
				assumed_revision = int(self._next_argument())
				self._set_assumed_revision(0, assumed_revision)
			elif arg == '--assume-rev2':
				assumed_revision = int(self._next_argument())
				self._set_assumed_revision(1, assumed_revision)
			elif arg == '--r1':
				assumed_revision = int(self._next_argument())
				self._set_assumed_revision(0, assumed_revision)
			elif arg == '--r2':
				assumed_revision = int(self._next_argument())
				self._set_assumed_revision(1, assumed_revision)
			elif re.match(r'--assume-rev1=\d+$', arg):
				assumed_revision = int(arg[14:])
				self._set_assumed_revision(0, assumed_revision)
			elif re.match(r'--assume-rev2=\d+$', arg):
				assumed_revision = int(arg[14:])
				self._set_assumed_revision(1, assumed_revision)
			elif re.match(r'--r1=\d+$', arg):
				assumed_revision = int(arg[5:])
				self._set_assumed_revision(0, assumed_revision)
			elif re.match(r'--r2=\d+$', arg):
				assumed_revision = int(arg[5:])
				self._set_assumed_revision(1, assumed_revision)
			elif arg == '-v':
				verbose = True
			else:
				raise Exception("Unknown argument: %r" % arg)
	
		for version in self._versions:
			if version.revision is not None and version.assumed_revision is not None:
				raise Exception("An assumed revision (%d) cannot be used with a revision (%d)" % (version.assumed_revision, version.revision))
	
		assert (self._versions[0].commit is None) or (self._versions[0].revision is None)
		assert (self._versions[1].commit is None) or (self._versions[1].revision is None)
		return self._versions[0], self._versions[1], verbose
	
	@staticmethod
	def _is_defined(version):
		return version.commit is not None or version.revision is not None

	def _set_commit(self, commit):
		for version in self._versions:
			if not self._is_defined(version):
				version.commit = commit
				return
		raise Exception("Too many _arguments")

	def _set_revision(self, revision):
		for version in self._versions:
			if not self._is_defined(version):
				version.revision = revision
				return
		raise Exception("Too many _arguments")

	def _set_assumed_revision(self, index, assumed_revision):
		if self._versions[index].assumed_revision is not None:
			raise Exception("Assumed revision already specified for the parameter")
		self._versions[index].assumed_revision = assumed_revision

	def _next_argument(self):
		if self._arguments:
			return self._arguments.pop(0)
		raise Expection("Expected argument")


class VersionsSolver(object):
	
	def __init__(self, cwd=None):
		self.cwd = cwd
	
	def solve_version1(self, version1):
		assert (version1.commit is None) or (version1.revision is None)
		assert (version1.revision is None) or (version1.assumed_revision is None)
		
		if not self._solve_common(version1):
			version1.commit = 'HEAD'
			if version1.assumed_revision is None:
				version1.assumed_revision = commit_to_revision(version1.commit, cwd=self.cwd)
		
		assert version1.commit is not None
		assert version1.assumed_revision is not None
	
	def solve_version2(self, version2):
		assert (version2.commit is None) or (version2.revision is None)
		assert (version2.revision is None) or (version2.assumed_revision is None)
		
		self._solve_common(version2)
		
		assert (version2.commit is None) == (version2.assumed_revision is None)
		
	def _solve_common(self, version):
		assert (version.commit is None) or (version.revision is None)
		assert (version.revision is None) or (version.assumed_revision is None)
		
		solved = False
		if version.commit is not None:
			if version.assumed_revision is None:
				version.assumed_revision = commit_to_revision(version.commit, cwd=self.cwd)
				if version.assumed_revision is None:
					raise NotImplementedError()
			solved = True
		elif version.revision is not None:
			version.commit = revision_to_commit(version.revision, cwd=self.cwd)
			if version.commit:
				version.assumed_revision = version.revision
			else:
				raise NotImplementedError()
			solved = True
		
		return solved


def process_arguments(): # TODO: remove
	revision1 = None
	revision2 = None
	verbose = False

	import sys
	args = sys.argv[1:]
	while args:
		arg = args.pop(0)
		if arg == '-r':
			if not args:
				raise Exception('Missing revision argument')
			arg = args.pop(0)
			if re.match(r'\d+$', arg):
				revision1 = int(arg)
			elif re.match(r'\d+:\d+$', arg):
				revision1, revision2 =  (int(rev) for rev in arg.split(':'))
			else:
				raise Exception('Invalid revision: %r' % arg)
		elif arg == '-v':
			verbose = True
		else:
			raise Exception('Unknown argument: %r' % arg)

	return revision1, revision2, verbose


def revision_to_commit(revision, cwd=None): # TODO: move to VersionSolver
	commit = find_rev('r%d' % revision, 'Revision', cwd)
	return commit


def commit_to_revision(commit, cwd=None): # TODO: move to VersionSolver
	revision = find_rev(commit, 'Commit', cwd)
	return int(revision)


def find_rev(param, what, cwd): # TODO: move to VersionSolver
	found = subprocess.check_output(['git', 'svn', 'find-rev', param], cwd=cwd)
	found = found.strip()
	if found == '':
		raise Exception(what + ' not found: %r' % param)
	return found


if __name__ == '__main__':
	main()
