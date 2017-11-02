#!/usr/bin/env python3
import sys
import getopt
import re
from parser import *
from type_checker import *
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

def main():
	input_file, output_file = command_line_parse()
	d_list = parser(input_file)
	function_dict, operation_list, qbit_set = type_check(d_list)
	print(function_dict)


if __name__ == '__main__':
    main()
