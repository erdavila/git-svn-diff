def run(impl):
	impl.save_file('emptied', 'Content of file\n')
	impl.save_file('deleted', 'Content of file\n')
	impl.add_new_file('emptied', 'deleted')
	impl.commit_all('Add files')

	impl.save_file('emptied', '')
	impl.remove_file('deleted')

	return []
