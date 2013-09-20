#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess


rev = 2   # TODO: get real value from somewhere


def main():
	output = subprocess.check_output(['git', 'diff', '--no-prefix'])
	lines = output.split('\n')
	for line in lines:
		line = re.sub(r'^diff --git (.+) \1$', r'Index: \1', line)
		line = re.sub(r'^index .+$', 67*'=', line)
		line = re.sub(r'^(--- .+)$', r'\1\t(revision %d)' % rev, line)
		line = re.sub(r'^(\+\+\+ .+)$', r'\1\t(working copy)', line)
		if line:
			print(line)


if __name__ == '__main__':
	main()
