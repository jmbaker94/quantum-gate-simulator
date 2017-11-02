from enum import Enum

class FuncType(Enum):
	MATRIX = 1
	SERIES = 2

class Function:
	def __init__(self, func_type = None, size = None, arg_list = None, func_content = None):
		self.func_type = func_type
		self.size = size
		self.arg_list = arg_list
		self.func_content = func_content
