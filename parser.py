#!/usr/bin/env python3
import sys
import re
from complexExp import *
from statement import *
from function import *
from register import *
from matrixData import *
# sys.path.appen("PATH TO GATE SIMULATOR")

def error(string):
	print("Line "+str(linenum)+": PARSING ERROR: "+string)
	sys.exit(3)

def read_token(f):
	string = ''
	c = f.read(1)
	global linenum
	while c==' ' or c=='\n' or c=='\t':
		c = f.read(1)
		if c == '\n':
			linenum+=1
	if c==';':
		string += c
		return string.rstrip()
	while c!=' ' and c!='\n' and c!='' and c!='\t' and c!=';':
		string+=c
		c = f.read(1)
		if c == '\n':
			linenum+=1
	if c==';':
		f.seek(f.tell()-1)
	return string.rstrip()

def expect(pattern, f):
	string = read_token(f)
	if string == pattern:
		return True
	else:
		f.close()
		return error("expected: "+pattern+", got: "+string)

def parser(input_file):
	global linenum
	linenum = 1
	f = open(input_file, 'r+')
	end = False
	success = True
	head_D, end = parse_D(f)
	current_D = head_D
	while(current_D and not end):
		next_D, end = parse_D(f)
		current_D.next = next_D
		current_D = next_D	

	if success and end:
		print("Parse Successful")
		return head_D
	else:
		print("Parse Failed")
		error()
		return None
	

def parse_D(f):
	savepos = f.tell()
	token = read_token(f)
	if token == '':
		return None, True
	if token == "gate":
		f_item = parse_F(f)
		t_item = parse_T(f)
		return Statement(StmtType.GATE_DEF, f_item, None, t_item, None), False
	elif token == "measure":
		r_item = parse_R(f)
		expect(';', f)
		return Statement(StmtType.MEASURE, None, None, None, r_item), False
	elif token == "inverse":
		f_final_item = parse_F(f)
		f_init_item = parse_F(f)
		expect(';', f)
		return Statement(StmtType.GATE_INV, f_final_item, f_init_item), False
	elif token == "circuit":
		c_item = parse_F(f)
		list_item = parse_L(f)
		expect("{", f)
		k_item = parse_K(f)
		expect("}", f)
		return Statement(StmtType.CIRCUIT, c_item, None, Function(FuncType.CIRCUIT, None, list_item, k_item), None), False
	elif token == "solve":
		c_item = parse_F(f)
		list_item = parse_L(f)
		expect(";", f)
		return Statement(StmtType.SOLVE, c_item, None, None, list_item), False
	else:
		f.seek(savepos)
		f_item = parse_F(f)
		list_item = parse_L(f)
		expect(';', f)
		return Statement(StmtType.GATE_USE, f_item, None, None, list_item), False

def parse_F(f):
	name = read_token(f)
	match = re.search('[A-Z]([A-Z0-9]|\_[A-Z0-9])*', name)
	if match:
		return match[0]
	else:
		f.close()
		return error(name+" does not follow gate or circuit name conventions")

def parse_R(f):
	register = read_token(f)
	match = re.search('[a-z][a-z0-9_]*', register)
	if match:
		return Register(match[0])
	else:
		f.close()
		return error(register+" does not follow register name conventions")
	
def parse_T(f):
	function = read_token(f)
	if function == "matrix":
		i_value = parse_I(f)
		r_value = parse_R(f)
		expect('{', f)
		m_value = parse_M(f)
		expect('}', f)
		return Function(FuncType.MATRIX, int(i_value), r_value, m_value) 
	elif function == "series":
		l_value = parse_L(f)
		expect('{', f)
		k_value = parse_K(f)
		expect('}', f)
		return Function(FuncType.SERIES, None, l_value, k_value)
	else:
		f.close()
		return error(function+" is not matrix or series type")

def parse_I(f):
	value = read_token(f)
	savepos = f.tell()
	match = re.search('[0-9]+', value)
	if match:
		f.seek(savepos-len(value)-1+len(match[0]))
		savepos = f.tell()
		f.seek(savepos)
		return match[0]
	else:
		f.close()
		return error("Expected Integer, got: "+value)

def parse_L(f):
	r_item = parse_R(f)
	next_item = parse_L_prime(f)
	r_item.next = next_item
	return r_item

def parse_L_prime(f):
	savepos = f.tell()
	string = read_token(f)	
	f.seek(savepos)
	if string==';' or string == '{':
		return None
	else:
		r_item = parse_R(f)
		next_item = parse_L_prime(f)
		r_item.next = next_item
		return r_item

def parse_M(f):
	matrix = MatrixElement(parse_J(f))
	matrix.next = parse_M_prime(f)
	return matrix

def parse_M_prime(f):
	savepos = f.tell()
	string = read_token(f)	
	f.seek(savepos)
	if string=='}':
		return None
	else:
		matrix = MatrixElement(parse_J(f))
		matrix.next = parse_M_prime(f)
		return matrix

def parse_J(f):
	e_item = parse_E(f)
	j_item = parse_J_prime(f)
	j_item.real = e_item
	return j_item

def parse_J_prime(f):
	savepos = f.tell()
	operation = read_token(f)
	if operation[0] == '+':
		f.seek(f.tell()-len(operation))
		e_item = parse_E(f)
		parse_Im(f)
		return Complex(ComplexType.ADD, None, e_item)
	elif operation[0] == '-':
		f.seek(f.tell()-len(operation))
		e_item = parse_E(f)
		parse_Im(f)
		return Complex(ComplexType.ADD, None, e_item)
	else:
		f.seek(savepos)
		return Complex(ComplexType.NONE, None, None)

def parse_E(f):
	savepos = f.tell()
	token = read_token(f)
	if token[0] == '-':
		f.seek(savepos+1)
		return token+parse_I(f)
	else:
		f.seek(savepos)
		return parse_I(f)

def parse_Im(f):
	token = read_token(f)
	if token == 'j' or token =='i':
		return token
	else:
		return error("imaginary value must be denoted by 'i' or 'j'")	

def parse_K(f):
	f_item = parse_F(f)
	l_item = parse_L(f)
	new_stmt = Statement(StmtType.GATE_USE, f_item, None, None, l_item)
	expect(';', f)
	new_stmt.next = parse_K_prime(f)
	return new_stmt

def parse_K_prime(f):
	savepos = f.tell()
	token = read_token(f)
	if token != '}':
		f.seek(savepos)
		f_item = parse_F(f)
		l_item = parse_L(f)
		new_stmt = Statement(StmtType.GATE_USE, f_item, None, None, l_item)
		expect(';', f)
		new_stmt.next = parse_K_prime(f)
		return new_stmt
	else:
		f.seek(savepos)
		return None