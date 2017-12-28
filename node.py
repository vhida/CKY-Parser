class Node:

	def __init__(self, root, left, right, end):

		self._root = root
		self._left = left
		self._right = right
		self._terminal = end
		self._status = True
		if end == None:
			self._status = False

	@property
	def root(self):
		return self._root

	@property
	def left(self):

		return self._left

	@property
	def right(self):

		return self._right

	@property
	def status(self):

		return self._status

	@property
	def terminal(self):

		return self._terminal