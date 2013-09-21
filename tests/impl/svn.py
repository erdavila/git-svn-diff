from __future__ import print_function
import os.path
import subprocess
from tempfile import mkdtemp

class SvnImpl(object):

	def __init__(self, suffix='-svn'):
		self.temp_path = mkdtemp(prefix='repo-', suffix=suffix)
		self.server_path = os.path.join(self.temp_path, 'server.svn')
		self.client_path = os.path.join(self.temp_path, 'client.svn')

		subprocess.check_call(['svnadmin', 'create', self.server_path])
		subprocess.check_call(['svn', 'checkout', 'file://' + self.server_path, self.client_path])
		
		self.save_file('dummy-file', '')
		self.add_new_file('dummy-file')
		self.commit_all('Initial commit')

	def save_file(self, filename, content):
		with open(os.path.join(self.client_path, filename), 'w') as f:
			f.write(content)

	def add_new_file(self, *files):
		subprocess.check_call(['svn', 'add'] + list(files), cwd=self.client_path)

	def remove_file(self, *files):
		subprocess.check_call(['svn', 'delete'] + list(files), cwd=self.client_path)

	def commit_all(self, message):
		subprocess.check_call(['svn', 'commit', '-m', message], cwd=self.client_path)
		subprocess.check_call(['svn', 'up'], cwd=self.client_path)

	def diff(self, *revs):
		assert len(revs) <= 2, len(revs)
		cmd = 'LANG=en_US.UTF-8 '  # Make sure output is in english
		cmd += 'svn diff'
		if revs:
			cmd += ' -r ' + ':'.join(str(rev) for rev in revs)

		diff_file = os.path.join(self.temp_path, 'svn.diff')
		with open(diff_file, 'w') as f:
			print("Executing %r" % cmd)
			subprocess.check_call(cmd, cwd=self.client_path, stdout=f, shell=True)
		return diff_file
