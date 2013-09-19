#!/usr/bin/env python
from __future__ import print_function
import imp
from impl.svn import SvnImpl


def main():
	import sys
	pathname = sys.argv[1]

	case = imp.load_source('case', pathname)
	svn_impl = SvnImpl()
	case.run(svn_impl)

	print("\nRepository is available at", svn_impl.temp_path)


if __name__ == '__main__':
	main()
