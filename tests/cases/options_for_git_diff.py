def run(impl):
	impl.save_file('file', 'First line\nThis is the second line\n')
	impl.add_new_file('file')
	impl.commit_all('Add files')

	impl.save_file('file', 'First line\nThis   is    the \tsecond  line  \nThe last line\n')

	return []
