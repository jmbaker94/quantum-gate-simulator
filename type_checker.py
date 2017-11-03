#!/usr/bin/env python3
import sys
import numpy as np
import cmath
from complexExp import *
from statement import *
from function import *
from register import *
from matrixData import *
# sys.path.appen("PATH TO GATE SIMULATOR")

def error(string):
	print("TYPE ERROR: "+string)

def type_check(d_list = None):
	if d_list == None:
		return None
	function_table = {
		"H": Function(None, None, Register("a"), None),
		"X": Function(None, None, Register("b"), None),
		"T": Function(None, None, Register("a", Register("b", Register("c"))), None),
	}
	qbit_set = set()
	circuit_table = {}
	operation_list = []
	if name_resolve_and_organize(d_list, function_table, circuit_table, qbit_set, operation_list):
		del function_table["H"]
		del function_table["T"]
		del function_table["X"]
		return function_table, operation_list, qbit_set
	else:
		print("Type Errors, please fix before continuing")
		sys.exit(4)

def name_resolve_and_organize(d_list, function_table, circuit_table, qbit_set, operation_list):
	current = d_list
	success = True
	while current:
		if StmtType.GATE_DEF == current.statement_type or StmtType.CIRCUIT == current.statement_type:
			if current.func_name in function_table:
				success = False
				error("redefinition of "+current.func_name)
			else:
				if StmtType.GATE_DEF == current.statement_type:
					if function_check(current.func_contents, current.func_name, function_table):
						function_table[current.func_name] = current.func_contents
				else:
					if function_check(current.func_contents, current.func_name, function_table):
						circuit_table[current.func_name] = current.func_contents
		elif StmtType.GATE_USE == current.statement_type:
			if current.func_name in function_table:
				if function_eq(current, function_table[current.func_name]):
					operation_list.append(current)
					qbit = current.reg_list
					while qbit:
						qbit_set.add(qbit.name)
						qbit = qbit.next
				else:
					error("incorrect number of arguments given to "+current.func_name)
					success = False
			else:
				success = False
				error("function name "+current.func_name+" does not exist")
		elif StmtType.GATE_INV == current.statement_type:
			if current.func_initial_name in function_table:
				if current.func_name in function_table:
					success = False
					error("redefinition of "+current.func_name)
				else:
					function_table[current.func_name] = Function(FuncType.OTHER, None, Register("a"), None)
				operation_list.append(current)
		elif StmtType.MEASURE == current.statement_type:
			qbit = current.reg_list
			qbit_set.add(qbit.name)
			operation_list.append(current)
		elif StmtType.SOLVE == current.statement_type:
			qbit = current.reg_list
			qbit_set.add(qbit.name)
			function_eq(current, circuit_table[current.func_name])
			operation_list.append(current)

		current = current.next
	return success

def function_check(function, function_name, function_table):
	success = True
	if function.func_type == FuncType.MATRIX:
		matrix_items = []
		matrix_element = function.func_content
		while matrix_element:
			matrix_items.append(matrix_element)
			matrix_element = matrix_element.next
		if len(matrix_items) != function.size*function.size:
			success = False
			error("Number of matrix elements does not match given matrix size")
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

		matrix = np.matrix(matrix)
		new_matrix = matrix.getH().transpose()

		if not np.array_equal(matrix, new_matrix):
			success = False
			error("matrix defined in "+function_name+" is not unitary")

	elif function.func_type == FuncType.SERIES or function.func_type == FuncType.CIRCUIT:
		qbit_list = set()
		qbit = function.arg_list
		while qbit:
			if qbit.name in qbit_list:
				error("redefinition of qbit "+qbit.name+", skipping...")
			else:
				qbit_list.add(qbit.name)
			qbit = qbit.next
		current = function.func_content
		while current:
			if current.func_name in function_table:
				if function_eq(current, function_table[current.func_name]):
					qbit = current.reg_list
					while qbit:
						if qbit.name not in qbit_list:
							error(qbit.name+" does not exist in function "+function_name)
						qbit = qbit.next
				else:
					error("incorrect number of arguments given to "+current.func_name)
					success = False
			else:
				success = False
				error("function name "+current.func_name+" does not exist")
			current = current.next
	else:
		success = False
		error("Unrecognized function type")
	
	return success

def function_eq(func1 = None, func2 = None):
	success = True
	length1 = get_length(func1.reg_list, True)
	length2 = get_length(func2.arg_list, False)
	if length1 != length2:
		success = False
	return success

def get_length(reg_list, count_repeat):
	if not count_repeat:
		reg_set = set()
	else:
		reg_set = []
	current = reg_list
	while current:
		if not count_repeat:
			reg_set.add(current.name)
		else:
			reg_set.append(current.name)
		current = current.next
	return len(reg_set)
