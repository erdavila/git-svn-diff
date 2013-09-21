import os.path
import subprocess
import shutil

class GitImpl(object):

	def __init__(self):
		from svn import SvnImpl

		svn_impl = SvnImpl(suffix='-git')
		shutil.rmtree(svn_impl.client_path)

		self.temp_path = svn_impl.temp_path
		self.server_path = svn_impl.server_path
		self.client_path = os.path.join(self.temp_path, 'client.git')

		subprocess.check_call(['git', 'svn', 'clone', 'file://' + self.server_path, self.client_path])

	def save_file(self, filename, content):
		with open(os.path.join(self.client_path, filename), 'w') as f:
			f.write(content)

	def add_new_file(self, *files):
		subprocess.check_call(['git', 'add'] + list(files), cwd=self.client_path)

	def remove_file(self, *files):
		subprocess.check_call(['git', 'rm'] + list(files), cwd=self.client_path)

	def commit_all(self, message):
		subprocess.check_call(['git', 'commit', '-a', '-m', message], cwd=self.client_path)
		subprocess.check_call(['git', 'svn', 'dcommit'], cwd=self.client_path)

	def diff(self, *revs):
		assert len(revs) <= 1

		if len(revs) == 0:
			revisions = ['HEAD']
		else:
			commit = subprocess.check_output(['git', 'svn', 'find-rev', 'r%d' % revs[0]], cwd=self.client_path)
			commit = commit.strip()
			assert commit != ''
			revisions = [commit]

		diff_file = os.path.join(self.temp_path, 'git.diff')
		with open(diff_file, 'w') as f:
			cmd = ['git', 'diff', '--no-prefix'] + revisions
			subprocess.check_call(cmd, cwd=self.client_path, stdout=f)
		return diff_file
