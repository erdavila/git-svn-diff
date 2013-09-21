#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess


class DiffTransformer(object):

	def __init__(self, revision):
		self.revision = revision

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
				rev = self.revision
			return '--- %s\t(revision %d)' % (self.filename, rev)
		elif line.startswith('+++ '):
			return '+++ %s\t(working copy)' % self.filename
		elif line.startswith('new file mode ') or line.startswith('deleted file mode '):
			return None
		else:
			return line


def main():
	revision = process_arguments()
	if revision is None:
		commit = 'HEAD'
		revision =  commit_to_revision(commit)
	else:
		commit = revision_to_commit(revision)

	cmd = ['git', 'diff', '--no-prefix', commit]
	output = subprocess.check_output(cmd)
	lines = output.splitlines()
	transformer = DiffTransformer(revision)
	for line in lines:
		line = transformer.transform_line(line)
		if line is not None:
			print(line)


def process_arguments():
	revision = None

	import sys
	args = sys.argv[1:]
	while args:
		arg = args.pop(0)
		if arg == '-r':
			if not args:
				raise Exception('Missing revision argument')
			arg = args.pop(0)
			if re.match(r'\d+$', arg):
				revision = int(arg)
			else:
				raise Exception('Invalid revision: %r' % arg)
		else:
			raise Exception('Unknown argument: %r' % arg)

	return revision


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
