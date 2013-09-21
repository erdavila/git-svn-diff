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
			return 67*'='
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
	revision = get_head_revision()
	output = subprocess.check_output(['git', 'diff', '--no-prefix', 'HEAD'])
	lines = output.split('\n')
	transformer = DiffTransformer(revision)
	for line in lines:
		line = transformer.transform_line(line)
		if line:
			print(line)


def get_head_revision():
	output = subprocess.check_output(['git', 'svn', 'info'])
	m = re.search(r'\nRevision: (\d+)\n', output)
	revision = int(m.group(1))
	return revision


if __name__ == '__main__':
	main()
