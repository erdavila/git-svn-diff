			return 67 * '='
	revision = process_arguments()
	if revision is None:
		commit = 'HEAD'
		revision =  commit_to_revision(commit)
	else:
		commit = revision_to_commit(revision)

	output = subprocess.check_output(['git', 'diff', '--no-prefix', commit])
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

