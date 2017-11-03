#!/usr/bin/env python3
import sys
import getopt
import re
from parser import *
from type_checker import *
from codegen import *
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
		print("error: too many arguments given")
		usage()
		sys.exit(2)
	elif len(args) < 1:
		print("error: No program given")
		usage()
		sys.exit(2)
	
	input_file = args[0]

	return input_file, output_file		

def main():
	input_file, output_file = command_line_parse()
	d_list = parser(input_file)
	function_dict, operation_list, qbit_set = type_check(d_list)
	if function_dict or operation_list or qbit_set:
		codegen(output_file, function_dict, operation_list, qbit_set)

if __name__ == '__main__':
    main()
