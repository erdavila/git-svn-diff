	def __init__(self, revision):
		self.revision = revision

				rev = 0
				rev = self.revision
			return '--- %s\t(revision %d)' % (self.filename, rev)
	revision = get_head_revision()
	lines = output.splitlines()
	transformer = DiffTransformer(revision)
		if line is not None:
def get_head_revision():
	output = subprocess.check_output(['git', 'svn', 'info'])
	m = re.search(r'\nRevision: (\d+)\n', output)
	revision = int(m.group(1))
	return revision

