#!/usr/bin/env python3
import sys
import time
import getopt
import re
# sys.path.appen("PATH TO GATE SIMULATOR")

def usage():
	print('''
	usage: qhdl.py [-h] [-o --output output_file] [--help]

	-h --help                 : Show usage statement
	-o --output=<output_file> : Use given output file
	''')

def command_line_parse():
	output_file = "a.py"
	input_file = ""
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'ho:', ["help", "output="])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(1)
	
	for o, a in opts:
		if o in ("-o", "--output"):
			output_file = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			usage()
			sys.exit(1)
	
	if len(args) > 1:
		print("Too many agruments given")
		usage()
		sys.exit(2)
	elif len(args) < 1:
		print("Error: No program given")
		usage()
		sys.exit(2)
	
	input_file = args[0]

	return input_file, output_file	

def read_token(f):
	string = ''
	c = f.read(1)
	while c==' ' or c=='\n' or c=='\t':
		c = f.read(1)
	if c==';':
		string += c
		return string.rstrip()
	while c!=' ' and c!='\n' and c!='' and c!='\t' and c!=';':
		string+=c
		c = f.read(1)
	if c==';':
		f.seek(f.tell()-1)
	return string.rstrip()

def expect(pattern, f):
	string = read_token(f)
	if string == pattern:
		return True
	else:
		return False

def parser(input_file):
	f = open(input_file, 'r+')
	end = False
	success = True
	while(success and not end):
		success, end = parse_D(f)

	if success and end:
		print("Parse Successful")
		return True
	else:
		print("Parse Failed")
		return False
	

def parse_D(f):
	savepos = f.tell()
	token = read_token(f)
	if token == '':
		return True, True
	if token == "gate":
		return parse_F(f) and parse_T(f), False
	elif token == "measure":
		return parse_R(f) and expect(';', f), False
	elif token == "inverse":
		return parse_F(f) and parse_F(f) and expect(';', f), False
	else:
		f.seek(savepos)
		return parse_F(f) and parse_L(f) and expect(';', f), False

def parse_F(f):
	name = read_token(f)
	match = re.search('[A-Z]([A-Z0-9]|\-[A-Z0-9])*', name)
	if match:
		return True
	else:
		return False

def parse_R(f):
	register = read_token(f)
	match = re.search('[a-z][a-z0-9_]*', register)
	if match:
		return True
	else:
		return False
	
def parse_T(f):
	function = read_token(f)
	if function == "matrix":
		i_value = parse_I(f)
		r_value = parse_R(f)
		between1 = expect('{', f)
		m_value = parse_M(f)
		between2 = expect('}', f)
		return i_value and r_value and between1 and m_value and between2
	elif function == "series":
		l_value = parse_L(f)
		between1 = expect('{', f)
		k_value = parse_K(f)
		between2 = expect('}', f)
		return l_value and between1 and k_value and between2
	else:
		return False

def parse_I(f):
	value = read_token(f)
	match = re.search('[0-9]+', value)
	if match:
		return True
	else:
		return False

def parse_L(f):
	return parse_R(f) and parse_L_prime(f)

def parse_L_prime(f):
	savepos = f.tell()
	string = read_token(f)	
	f.seek(savepos)
	if string==';' or string == '{':
		return True
	else:
		return parse_R(f) and parse_L_prime(f)

def parse_M(f):
	return parse_J(f) and parse_M_prime(f)

def parse_M_prime(f):
	savepos = f.tell()
	string = read_token(f)	
	f.seek(savepos)
	if string=='}':
		return True
	else:
		return parse_J(f) and parse_M_prime(f)

def parse_J(f):
	return parse_E(f) and parse_J_prime(f)

def parse_J_prime(f):
	savepos = f.tell()
	operation = read_token(f)
	if operation == '+':
		return parse_E(f) and parse_Im(f)
	elif operation == '-':
		return parse_E(f) and parse_Im(f)
	else:
		f.seek(savepos)
		return True

def parse_E(f):
	savepos = f.tell()
	token = read_token(f)
	if token == '-':
		return parse_I(f)
	else:
		f.seek(savepos)
		return parse_I(f)

def parse_Im(f):
	token = read_token(f)
	if token == 'j' or token =='i':
		return True
	else:
		return False	

def parse_K(f):
	return parse_F(f) and parse_L(f) and expect(';', f) and parse_K_prime(f)

def parse_K_prime(f):
	savepos = f.tell()
	token = read_token(f)
	if token != '}':
		f.seek(savepos)
		return parse_F(f) and parse_L(f) and expect(';', f) and parse_K_prime(f)
	else:
		f.seek(savepos)
		return True
	

def main():
	input_file, output_file = command_line_parse()
	parser(input_file)

if __name__ == '__main__':
    main()
