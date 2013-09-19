def run(impl):
	impl.save_file('a', 'Content of file a\n')
	impl.save_file('b', 'Content of file b\n')
	impl.add('a', 'b')
	impl.commit_all('Initial commit')

	impl.save_file('a', 'Content of file a\nA new line at the end\n')
	impl.save_file('b', 'Changed content of file b\n')
