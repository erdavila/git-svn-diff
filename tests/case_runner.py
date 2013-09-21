from __future__ import print_function
import imp

def run(impl):
	import sys
	pathname = sys.argv[1]

	case = imp.load_source('case', pathname)
	revs = case.run(impl)
	diff_file = impl.diff(*revs)
	print('Diff saved to', diff_file)
