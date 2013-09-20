#!/usr/bin/env python
from __future__ import print_function
import os.path
import subprocess
import unittest
from impl.git import GitImpl
import cases.multiple_changes


class Test(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testName(self):
		git_impl = GitImpl()
		cases.multiple_changes.run(git_impl)
		# TODO: resolve path
		output = subprocess.check_output(["/home/erdavila/Projetos/git-svn-diff/git_svn_diff.py"], cwd=git_impl.client_path)
		expected_output = \
'''Index: a
===================================================================
--- a	(revision 2)
+++ a	(working copy)
@@ -1 +1,2 @@
 Content of file a
+A new line at the end
Index: b
===================================================================
--- b	(revision 2)
+++ b	(working copy)
@@ -1 +1 @@
-Content of file b
+Changed content of file b
'''
		with open(os.path.join(git_impl.temp_path, 'git-svn-diff.output'), 'w') as f:
			f.write(output)
		with open(os.path.join(git_impl.temp_path, 'svn-diff.output'), 'w') as f:
			f.write(expected_output)
		self.assertEqual(expected_output, output)


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()
