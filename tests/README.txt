To create a new test case:
	- Create the case in cases/<new-test-case>.py
	- Execute the case:
		./run_svn_case.py cases/<new-test-case>.py
	- See the last line of the output and copy the file:
		cp /tmp/repo-<something>-svn/svn.diff expected/<new-test-case>.diff
	- Add the test method test<NewTestCase> to run_tests.py
	- Execute the test:
		./run_tests.py Test.test<NewTestCase>
	- Make it work!
		Somewhere in the console output the temporary directory
		/tmp/repo-<something>-git/ is mentioned. This directory contains:
			- git-svn.diff - The generated output.
			- svn.diff - The expected output (a copy of expected/<new-test-case>.diff).
	- Make sure all tests pass:
		./run_tests.py
