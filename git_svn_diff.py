			return 67*'='
			if line == '--- /dev/null':
				r = 0
			else:
				r = rev
			return '--- %s\t(revision %d)' % (self.filename, r)
			return '+++ %s\t(working copy)' % self.filename
		elif line.startswith('new file mode ') or line.startswith('deleted file mode '):