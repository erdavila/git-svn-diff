git-svn-diff
============
Generate an SVN-formatted diff from a Git diff.

Usage
-----
Execute with the `--help` option to learn what options can be used.

Installation
------------
I suggest two alternatives:
* Copy the `git_svn_diff.py` file to some directory in your `$PATH`
* Or create a Git alias:
  `git config alias.svn-diff <PATH-TO>/git_svn_diff.py`

Why It Was Developed?
---------------------
I was working on a project with files hosted by SVN, but I was using git-svn. There was a code review tool
that accepted only strictly SVN-formatted diff files, so I needed something to convert the Git diffs to a
format that the tool would accept. And then this script was born!
