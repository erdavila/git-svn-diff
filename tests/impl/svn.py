import os.path
import subprocess
from tempfile import mkdtemp

class SvnImpl(object):

	def __init__(self):
		self.temp_path = mkdtemp(prefix='svnrepo-')
		self.server_path = os.path.join(self.temp_path, 'server')
		self.client_path = os.path.join(self.temp_path, 'client')

		subprocess.check_call(['svnadmin', 'create', self.server_path])
		subprocess.check_call(['svn', 'checkout', 'file://' + self.server_path, self.client_path])

	def save_file(self, filename, content):
		with open(os.path.join(self.client_path, filename), 'w') as f:
			f.write(content)

	def add(self, *files):
		subprocess.check_call(['svn', 'add'] + list(files), cwd=self.client_path)

	def commit_all(self, message):
		subprocess.check_call(['svn', 'commit', '-m', message], cwd=self.client_path)
		subprocess.check_call(['svn', 'up'], cwd=self.client_path)
