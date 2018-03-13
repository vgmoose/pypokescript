#!/usr/bin/python3
# CLI for pypokescript

import sys, os

try:
	from .PokeScript import PokeScript
except:
	print("Missing module (pypokescript), ensure it is installed")
	exit(-9)

if len(sys.argv) <= 1:
	print("Usage: python %s 6_1194")
	print("\tIf script file is specified, text will be the output")
	print("Usage: python %s 6_1194.txt")
	print("\tIf a .txt is specified (must use .txt extension), a script file hex will be the output")
	print("--> Extract the B2W2 script from a/0/5/6 using NitroExplorer or kiwids")
	print("--> You can use PPNFR to replace \"File 1194\" in 6.narc")
	exit(-1)
	
# parse it as either text/data and output it as the opposite
	
if sys.argv[1].lower().endswith(".txt"):
	# text given, load as text
	script = PokeScript(sys.argv[1])
	fp = os.fdopen(sys.stdout.fileno(), 'wb')
	fp.write(script.getBytes())
else:
	# assume script given, load as data
	script = PokeScript(sys.argv[1])
	print(script.getText())