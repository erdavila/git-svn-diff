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


def process_arguments():
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


def revision_to_commit(revision):
	commit = find_rev('r%d' % revision, 'Revision')
	return commit


def commit_to_revision(commit):
	revision = find_rev(commit, 'Commit')
	return int(revision)


def find_rev(param, what):
	found = subprocess.check_output(['git', 'svn', 'find-rev', param])
	found = found.strip()
	if found == '':
		raise Exception(what + ' not found: %r' % param)
	return found


if __name__ == '__main__':
	main()
