#!/usr/bin/python3
# CLI for pypokescript

import sys, os

from .games.utils import nds

try:
	from .PokeScript import PokeScript
except:
	print("Missing module (pypokescript), ensure it is installed")
	exit(-9)

print("[PyPokeScript]")
print("Run one of the below tools for usage info:")
print("python3 -m pypokescript.PokeScript")
print("\t- convert to/from b2w2 pokescript and text files")
print("python3 -m pypokescript.games.utils.nds")
print("\t- extract/write/list files in .nds file")
