#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess
import sys


class DiffTransformer(object):

	def __init__(self, revision1, revision2):
		self.revision1 = revision1
		self.revision2 = revision2
	
	def transform_lines(self, lines):
		for line in lines:
			line = line.rstrip('\r\n')
			line = self.transform_line(line)
			if line is not None:
				yield line

	def transform_line(self, line):
		if line.startswith('diff --git '):
			m = re.search(r'^diff --git (.+) \1$', line)
			if m:
				self.filename = m.group(1)
			else:
				m = re.search(r'^diff --git a/(.+) b/\1$', line)
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
	args_parser = ArgumentsParser()
	version1, version2, verbose = args_parser.parse(sys.argv[1:])
	
	convert_from_pipe = convert_from_pipe_arguments(version1, version2)
	
	if convert_from_pipe:
		lines = sys.stdin
	else:
		versions_solver = VersionsSolver()
		versions_solver.solve_version1(version1)
		versions_solver.solve_version2(version2)
		
		commits = [version1.commit]
		if version2.commit is not None:
			commits.append(version2.commit)
		
		cmd = ['git', 'diff', '--no-prefix'] + commits
		if verbose:
			print('Executing %r' % cmd, file=sys.stderr)
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		process.poll()
		if process.returncode not in (None, 0):
			raise NotImplementedError()
		lines = process.stdout
		
	transformer = DiffTransformer(version1.assumed_revision, version2.assumed_revision)
	for line in transformer.transform_lines(lines):
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
			elif arg in ('-h', '--help'):
				show_help()
				sys.exit()
			elif arg.startswith('-'):
				raise Exception("Unknown argument: %r" % arg)
			else:
				self._set_commit(arg)
	
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


def convert_from_pipe_arguments(version1, version2):
	return version1.commit is None \
	   and version1.revision is None \
	   and version1.assumed_revision is not None \
	   and version2.commit is None \
	   and version2.revision is None \
	   and not sys.stdin.isatty()


class VersionsSolver(object):
	
	def __init__(self, cwd=None):
		self._cwd = cwd
	
	def solve_version1(self, version1):
		assert (version1.commit is None) or (version1.revision is None)
		assert (version1.revision is None) or (version1.assumed_revision is None)
		
		if not self._solve_common(version1):
			version1.commit = 'HEAD'
			if version1.assumed_revision is None:
				version1.assumed_revision = self._commit_to_revision(version1.commit)
		
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
				version.assumed_revision = self._commit_to_revision(version.commit)
				if version.assumed_revision is None:
					raise NotImplementedError()
			solved = True
		elif version.revision is not None:
			version.commit = self._revision_to_commit(version.revision)
			if version.commit:
				version.assumed_revision = version.revision
			else:
				raise NotImplementedError()
			solved = True
		
		return solved
	
	def _revision_to_commit(self, revision):
		commit = self._find_rev('r%d' % revision, 'Revision')
		return commit
	
	def _commit_to_revision(self, commit):
		revision = self._find_rev(commit, 'Commit')
		return int(revision)
	
	def _find_rev(self, param, what):
		found = subprocess.check_output(['git', 'svn', 'find-rev', param], cwd=self._cwd)
		found = found.strip()
		if found == '':
			raise Exception(what + ' not found: %r' % param)
		return found


def show_help():
	text = \
	"""Generate an SVN-formated diff.

Commands:
	git_svn_diff.py [-v] [<version> [<version>]]
		Compare two versions.

	git diff <options> | git_svn_diff.py [-v] --assume-rev1=REV1 [--assume-rev2=REV2]
		Convert a Git diff to SVN diff.

	A version may be either:
		* An SVN revision REV specified in either form:
			-r REV
			rREV
		  When comparing two SVN revisions REV1 and REV2, they can be specified with the argument:
			-r REV1:REV2
		  Must be in a git-svn repository to specify an SVN revision.
		* A Git commit.
		  An additional corresponding option can be used to specify the assumed SVN revision:
			--assume-rev1=REV1 (for the first version to compare)
			--assume-rev2=REV2 (for the second version to compare)
		  If not specifying an assumed revision, then the repository must be a git-svn repository and the commit must have been fetched from or dcommitted to an SVN server.
	
	If the first version is not informed, the HEAD commit is considered.
	If the second version is not informed, the working dir is considered.

	In the second form, if --assume-rev2 (or --r2) is not specified, the working dir is considered as the second version.

	The options --assume-rev1 and --assume-rev2 can be passed as --r1 and --r2.

	-v  Displays verbose output.

	-h or --help
		Displays this help message.
"""
	rows, columns = (int(value) for value in subprocess.check_output(['stty', 'size']).strip().split())
	
	import textwrap
	wrapper = textwrap.TextWrapper(width=columns-2)
	
	def remove_indent(line):
		indent = 0
		index = 0
		for index, char in enumerate(line):
			if char == ' ':
				indent += 1
			elif char == '\t':
				indent += 4
			else:
				break
		
		return indent, line[index:]
	
	for line in text.splitlines():
		indent, content = remove_indent(line)
		wrapper.initial_indent = wrapper.subsequent_indent = indent * ' '
		if content:
			for content_line in wrapper.wrap(content):
				print(content_line)
		else:
			print()


if __name__ == '__main__':
	main()
