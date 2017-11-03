#!/usr/bin/env python3
import sys
from type_checker import get_length
from complexExp import *
from statement import *
from function import *
from register import *
from matrixData import *

def codegen(output_file = None, function_dict = None, operation_list = None, qbit_set = None):
	f = open(output_file, 'w')
	add_imports(f)
	add_functions(f, function_dict)
	create_main(f, function_dict, operation_list, qbit_set)
	add_init(f)
	f.close()

def add_imports(f):
	f.write("#!/usr/bin/env python3\n")
	f.write("from qc_simulator import *\n")
	f.write("\n")

def add_functions(f, function_dict):
	for function in function_dict.keys():
		create_function(f, function_dict, function_dict[function], function)

def create_function(f, function_dict, function, func_name):
	f.write("def "+func_name+"(")
	if function.func_type == FuncType.MATRIX:
		f.write("qbit: QBit):\n")
		matrix_items = []
		matrix_element = function.func_content
		while matrix_element:
			matrix_items.append(matrix_element)
			matrix_element = matrix_element.next
		matrix  = []
		row = []
		for index, element in enumerate(matrix_items, 1):
			real = int(element.element.real)

			if not element.element.imag:
				imag = 0
			else:
				imag = int(element.element.imag)

			if element.element.math_type == ComplexType.ADD:
				number = real + imag*1j
			elif element.element.math_type == ComplexType.SUB:
				number = real + imag*1j
			else:
				number = real + imag*1j

			row.append(number)
			if index % function.size == 0:
				matrix.append(row)
				row = []

		f.write("\tT = np.matrix([")
		for row_item in range(len(matrix)):
			if row_item < len(matrix)-1:
				f.write(str(matrix[row_item])+", ")
			else:
				f.write(str(matrix[row_item])+"])\n")
		f.write("\tqbit.vector = np.dot(T, qbit.vector)")

		f.write("\n")
	elif function.func_type == FuncType.SERIES:
		f.write("qstate: QState):\n")
		arg = function.arg_list
		length = 0
		arg_list = []
		while(arg):
			if arg.name not in arg_list:
				length+=1
				arg_list.append(arg.name)
			arg = arg.next
		f.write("\tif len(qstate) != "+str(length)+":\n")
		f.write("\t\traise BadLengthError\n")
		operation = function.func_content
		while operation:
			if StmtType.GATE_USE == operation.statement_type:
				if operation.func_name == "H":
					f.write("\thadamard("+"qstate["+str(arg_list.index(operation.reg_list.name))+"]"+")\n")
				elif operation.func_name == "T":
					f.write("\tToffoli(QState([")
					reg = operation.reg_list
					while reg.next:
						f.write("qstate["+str(arg_list.index(reg.name))+"], ")
						reg = reg.next
					f.write("qstate["+str(arg_list.index(reg.name))+"]")
					f.write("]))\n")
				elif operation.func_name == "X":
					f.write("\tpauli_x(qstate["+str(arg_list.index(operation.reg_list.name))+"])\n")
				else:
					if function_dict[operation.func_name].func_type==FuncType.MATRIX:
						f.write("\t"+operation.func_name+"(qstate["+str(arg_list.index(operation.reg_list.name))+"])\n")
					else:
						f.write("\t"+operation.func_name+"(QState([")
						reg = operation.reg_list
						while reg.next:
							f.write("qstate["+str(arg_list.index(reg.name))+"], ")
							reg = reg.next
						f.write("qstate["+str(arg_list.index(reg.name))+"]")
						f.write("]))\n")
			operation = operation.next
	else:
		f.write("):\n\tpass\n")
	f.write("\n")


def create_main(f, function_dict, operation_list, qbit_set):
	f.write("def main():\n")
	for qbit in qbit_set:
		f.write("\t"+qbit+" = QBit()\n")
	f.write("\n")
	for operation in operation_list:
		if StmtType.GATE_USE == operation.statement_type:
			if operation.func_name == "H":
				f.write("\thadamard("+operation.reg_list.name+")\n")
			elif operation.func_name == "T":
				f.write("\tToffoli(QState([")
				reg = operation.reg_list
				while reg.next:
					f.write(reg.name+", ")
					reg = reg.next
				f.write(reg.name)
				f.write("]))\n")
			elif operation.func_name == "X":
				f.write("\tpauli_x("+operation.reg_list.name+")\n")
			else:
				if function_dict[operation.func_name].func_type==FuncType.MATRIX:
					f.write("\t"+operation.func_name+"("+operation.reg_list.name+")\n")
				else:
					f.write("\t"+operation.func_name+"(QState([")
					reg = operation.reg_list
					while reg.next:
						f.write(reg.name+", ")
						reg = reg.next
					f.write(reg.name)
					f.write("]))\n")
		elif StmtType.GATE_INV == operation.statement_type:
			f.write("\tinverse("+operation.func_name+", "+operation.func_initial_name+")\n")
		elif StmtType.MEASURE == operation.statement_type:
			f.write("\tmeasure("+operation.reg_list.name+")\n")
		elif StmtType.SOLVE == operation.statement_type:
			f.write("\tsolve("+")\n")
	f.write("\n")

def add_init(f):
	f.write("if __name__ == '__main__':\n\tmain()")