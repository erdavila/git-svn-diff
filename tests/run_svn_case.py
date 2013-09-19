#!/usr/bin/env python
import case_runner
from impl.svn import SvnImpl


def main():
	svn_impl = SvnImpl()
	case_runner.run(svn_impl)


if __name__ == '__main__':
	main()
