#!/bin/python

import sys

if len(sys.argv) <= 1:
	print("Usage: python %s 6_1194")
	print("\tIf script file is specified, text will be the output")
	print("Usage: python %s 6_1194.txt")
	print("\tIf a .txt is specified (must use .txt extension), a script file hex will be the output")
	print("--> Extract the B2W2 script from a/0/5/6 using NitroExplorer or kiwids")
	print("--> You can use PPNFR to replace \"File 1194\" in 6.narc")
	exit(-1)
	
# make value -> key pairs in incoming dict
def doublyLink(m):
	keys = list(m.keys())
	vals = list(m.values())
	for x in range(len(keys)):
		m[vals[x]] = keys[x]

# command : (name, arguments)
# thanks to Kaphotics: http://pastebin.com/raw/vrkp0SN8
commands = {
	0x0064: ("ApplyMovement", 3),
	0x002e: "LockAll",
	0x0003: ("ReturnAfterDelay", 1),
	0x0143: ("MoveCamera", 9),
	0x0065: "WaitMovement",
	0x0141: "LockCamera",
	0x013f: "StartCameraEvent",
	0x0145: "EndCameraEvent",
	0x01a3: "FlashBlackInstant",
	0x01a7: "Xtransciever7",
	0x003c: ("Message", 5),
	0x003f: "CloseMessageKeyPress2",
	0x00b3: ("FadeScreen", 4),
	0x00b4: "ResetScreen",
	0x01ac: "FadeIntoBlack",
	0x0142: "ReleaseCamera",
	0x0140: "StopCameraEvent",
	0x00c4: ("TeleportWarp", 5),
	0x0030: "WaitMoment",
	0x002f: "UnlockAll",
	0x0002: "ScriptDelimiter"
}

doublyLink(commands)

# assume all of these take 1 argument,
# again thanks to Kaphotics: http://pastebin.com/raw/tJXgpmYA
moves = {
	0x0000: "FaceUp",
	0x0001: "FaceDown",
	0x0002: "FaceLeft",
	0x0003: "FaceRight",
	0x000c: "WalkUp",
	0x000d: "WalkDown",
	0x000e: "WalkLeft",
	0x000f: "WalkRight",
	0x0020: "NoMove3Up",
	0x0021: "NoMove3Down",
	0x0022: "NoMove3Left",
	0x0023: "NoMove3Right",
	0x004b: "Exclamation!",
	0x009f: "Question?",
	0x00fe: "EndMovement",
	0x0045: "Vanish",
	0x00b9: "ShadowTriadOut",
	0x0046: "Reappear",
	0x00b8: "ShadowTriadIn"
}

doublyLink(moves)

class Move:
	def setCode(self, code, args):
		self.code = code
		self.args = args
		
		if code in moves:
			self.name = moves[code]
		else:
			self.name = "%04x" % code
	def setName(self, name):
		pass
	
	def printText(self):
		print("%s %04x" % (self.name, self.args))

class Movement:
	def __init__(self, label, pos):
		self.moves = []
		self.label = label
		self.pos = pos

class Command:
	def __init__(self):
		self.args = []
		self.arg_count = 0
	def setName(self, name):
		self.name = name
		self.code = commands[name]
		
	# load the name from a given code
	# also updates the number of arguments for the given code
	def setCode(self, code):
		self.code = code
		
		# if the code is a known command
		if code in commands:
			name = commands[code]
			
			# return arguments if there are any
			if type(name) is tuple:
				self.name = name[0]
				self.arg_count = name[1]
			else:
				# single arg, just assign name
				self.name = name
		else:
			# not found, use opcode
			self.name = "%04x" % self.code
	
	def getText(self):
		ret = self.name
		if self.args:
			for arg in self.args:
				if type(arg) is str:
					ret += " " + arg
				else:
					ret += " %04x" % arg
		return ret
			

class PokeScript:
	def __init__(self):
		self.commands = []
		self.movements = []
		
	def printText(self):
		for command in self.commands:
			print(command.getText())
		
		for movement in self.movements:
			print("%s: " % movement.label)
			for move in movement.moves:
				move.printText()
	
	def loadBytes(self, text):
		data = text.read()
		
		last_cmd = None
		pos_so_far = len(data)
		seen_delimiter = False
		
		# process commands and codes
		for b in range(0, len(data), 2):
			# get code as reverse-endian
			code = int("%02x%02x" % (data[b+1], data[b]), 16)
			
			# if there's any arg_count leftover,
			# add this code to the last command
			if last_cmd and last_cmd.arg_count > len(last_cmd.args):
				last_cmd.args.append(code)
				continue
			
			# create a command object for this opcode
			last_cmd = Command()
			
			# load code into object, get argument count
			last_cmd.setCode(code)
			last_cmd.pos = b			# offset of cmd in file
			
			self.commands.append(last_cmd)
			
			if last_cmd.name == "ScriptDelimiter":
				if seen_delimiter:
					# already seen the delimiter once,
					# so we proceed to processing movements
					pos_so_far = b + 2
					break
				else:
					# saw first delimiter, start of script probably
					seen_delimiter = True
			
		# process movements, 4 bytes at a time
		cur_moves = []
		pos_start = pos_so_far		# start pos for cur_moves batch
		
		for b in range(pos_so_far, len(data), 4):
			# get movement code
			code = int("%02x%02x" % (data[b+1], data[b]), 16)
			args = int("%02x%02x" % (data[b+3], data[b+2]), 16)
			
			move = Move()
			move.setCode(code, args)
			cur_moves.append(move)
			
			if move.name == "EndMovement":
				# end movement found, commit moves+movement to script
				movement = Movement("Movement%00d" % len(self.movements), pos_start)
				movement.moves = cur_moves
				self.movements.append(movement)
				cur_moves = []
				pos_start = b + 4
			
		# go through commands, find ones that are ApplyMovement
		for cmd in self.commands:
			if cmd.name == "ApplyMovement":
				# replace the 2nd arg with a movement label
				# we can just discard the original offset, since the
				# text only cares about the label
				offset = cmd.args[1] + 8 + cmd.pos
#				print(offset, [m.pos for m in self.movements])
				
				cmd.args[1] = "UNKNOWN"
				
				# try to find offset in movements
				for movement in self.movements:
					if movement.pos == offset:
						cmd.args[1] = movement.label
						break
			
# create a PokeScript object
script = PokeScript()

# parse it as either text/data and output it as the opposite
	
if sys.argv[1].lower().endswith(".txt"):
	# text given, load as text
	with open(sys.argv[1], "r") as text:
		script.loadText(text)
		script.printBytes()
else:
	# assume script given, load as data
	with open(sys.argv[1], "rb") as data:
		script.loadBytes(data)
		script.printText()
		
