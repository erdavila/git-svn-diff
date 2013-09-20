#!/usr/bin/env python
import case_runner
from impl.git import GitImpl


def main():
	git_impl = GitImpl()
	case_runner.run(git_impl)


if __name__ == '__main__':
	main()
