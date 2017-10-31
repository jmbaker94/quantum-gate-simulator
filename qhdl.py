#!/usr/bin/env python3
import sys
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

def read_to_white(f):
	string = ''
	while(f.peek(1)!=' '):
		c = f.read(1)
		string+=1
	return string

def read_to_non_white(f):
	while(f.peek(1)==' '):
		c = f.read(1)

def expect(pattern, f):
	

def parser(input_file):
	f = open(input_file, 'w')
	end = False
	success = True
	while(success and not end):
		success, end = parse_D(f)

def parse_D(f):
	read_to_non_white(f)
	if f.peek(1) == '':
		return True, True
	function = f.peek(4)
	if function == "gate":
		read_to_white(f)
		read_to_non_white(f)
		return parse_F(f) and parse_T(f) and expect(';', f), False
	else:
		return parse_F(f) and parse_R(f) and expect(';', f), False

def parse_F(f):
	name = read_to_white(f)
	match = re.search('[A-Z]([A-Z0-9]|\-[A-Z0-9])', name)
	if match:
		return True
	else return False
	
def parse_T(f):
	read_to_non_white(f)
	function = read_to_white(f)
	if function == "matrix":
		i_value = parse_I(f)
		l_value = parse_L(f)
		between1 = expect('{', f)
		m_value = parse_M(f)
		between2 = expect('}', f)
		return i_value and l_value and between1 and m_value and between2
	elif function == "series":
		l_value = parse_L(f)
		between1 = expect('{', f)
		k_value = parse_K(f)
		between2 = expect('}', f)
		return i_value and between1 and k_value and between2
	else:
		return False

def parse_I(f):
	read_to_non_white(f)
	value = read_to_white(f)
	match = re.search('[0-9]+', value)
	if match:
		return True
	else:
		return False

def parse_L(f):
	return parse_R(f) and parse_L_prime(f)

def parse_L_prime(f)
	if f.peek(1)==' ':
		return True
	else:
		return parse_R(f) and parse_L_prime(f)

def main():
	input_file, output_file = command_line_parse()

if __name__ == '__main__':
    main()
