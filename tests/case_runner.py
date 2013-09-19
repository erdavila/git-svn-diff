from __future__ import print_function
import imp

def run(impl):
	import sys
	pathname = sys.argv[1]

	case = imp.load_source('case', pathname)
	case.run(impl)

	print("\nRepository is available at", impl.temp_path)
