def run(impl):
	impl.save_file('a', 'Content of file a\n')
	impl.save_file('b', 'Content of file b\n')
	impl.add_new_file('a', 'b')
	impl.commit_all('Add files')

	impl.save_file('a', 'Content of file a\nA new line at the end\n')
	impl.save_file('b', 'Changed content of file b\n')

	return []
