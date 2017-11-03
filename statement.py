from enum import Enum

class StmtType(Enum):
	GATE_USE = 1
	GATE_DEF = 2
	GATE_INV = 3
	CIRCUIT = 4
	MEASURE = 5
	SOLVE = 6

class Statement:
	def __init__(self, statement_type = None, func_name = None, func_initial_name = None, func_contents = None, reg_list = None):
		self.statement_type = statement_type
		self.func_name = func_name
		self.func_initial_name = func_initial_name
		self.func_contents = func_contents
		self.reg_list = reg_list
		self.next = None
