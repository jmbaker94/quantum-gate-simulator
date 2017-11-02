from enum import Enum

class ComplexType(Enum):
	ADD = 1
	SUB = 2
	NONE = 3

class Complex:
	def __init__(self, math_type = None, real = None, imag = None):
		self.math_type = math_type
		self.real = real
		self.imag = imag
