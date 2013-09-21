def run_changes(impl):
	impl.save_file('a', 'Content of file a in revision 2\n')
	impl.save_file('b', 'Content of file b in revision 2\n')
	impl.add_new_file('a', 'b')
	impl.commit_all('Add files')  # revision 2

	impl.save_file('a', 'Content of file a in revision 3\n')
	impl.save_file('c', 'Content of file c in revision 3\n')
	impl.add_new_file('c')
	impl.commit_all('Change a and add c')  # revision 3

	impl.save_file('b', 'Content of file b in working dir\n')
	impl.save_file('c', 'Content of file c in working dir\n')
	impl.save_file('d', 'Content of file d in working dir\n')
	impl.add_new_file('d')
