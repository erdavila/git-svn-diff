#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess


rev = 2   # TODO: get real value from somewhere


class DiffTransformer(object):

	def transform_line(self, line):
		if line.startswith('diff --git '):
			m = re.search(r'^diff --git (.+) \1$', line)
			self.filename = m.group(1)
			return 'Index: ' + self.filename
		elif line.startswith('index '):
			return re.sub(r'^index .+$', 67*'=', line)
		elif line.startswith('--- '):
			if line == '--- /dev/null':
				return '--- %s\t(revision 0)' % self.filename
			else:
				return re.sub(r'^(--- .+)$', r'\1\t(revision %d)' % rev, line)
		elif line.startswith('+++ '):
			if line == '+++ /dev/null':
				return '+++ %s\t(working copy)' % self.filename
			else:
				return re.sub(r'^(\+\+\+ .+)$', r'\1\t(working copy)', line)
		elif line.startswith('new file mode ') or line.startswith('deleted file mode '):
			return None
		else:
			return line


def main():
	output = subprocess.check_output(['git', 'diff', '--no-prefix', 'HEAD'])
	lines = output.split('\n')
	transformer = DiffTransformer()
	for line in lines:
		line = transformer.transform_line(line)
		if line:
			print(line)


if __name__ == '__main__':
	main()
