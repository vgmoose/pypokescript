import sys, os

from .games.b2w2 import b2w2
from .Command import Command
from .Movement import Movement
from .Move import Move
from .utils import s

# game mode forced to b2w2
game = b2w2()
commands = game.commands
moves = game.moves

# this object represents a b2w2 pokescript file
# it contains method sthat can turn a txt file into the binary to be injected
# into the narc, and vice versa
class PokeScript:
	def __init__(self, incoming=None, isPath=True):
		self.commands = []
		self.variables = {}
		self.movements = []

		if isPath and incoming:
			if incoming.lower().endswith(".txt"):
				# if path is provided, read text from it
				with open(incoming, "r") as text:
					self.loadText(text)
			else:
				with open(incoming, "rb") as data:
					self.loadBytes(data)
		else:
			# assume it's binary data incoming
			self.loadBytes(incoming, False)

	# return the pokescript .txt representation of this object
	def getText(self):
		ret = []

		ret.append("# actor variables\n")
		for variable in self.variables:
			ret.append("%s = %s\n" % (variable, self.variables[variable]))

		ret.append("\n# script commands\n")
		for command in self.commands:
			ret.append(command.getText() + "\n")

		ret.append("\n# movement data\n")
		for movement in self.movements:
			ret.append("%s: \n" % movement.label)
			for move in movement.moves:
				ret.append("\t%s\n" % move.getText())

		return "".join(ret)

	# return the ready-to-inject hex of bytes of this object
	def getBytes(self):
		ret = bytearray()

		# find out the length of the commands portion
		size = 0
		for command in self.commands:
			size += 2 + len(command.args)*2

		for command in self.commands:
			ret.extend(s(command.code))
			arg_copy = command.args[:]

			# handle special logic to resolve movement labels
			if command.name == "ApplyMovement":
				for movement in self.movements:
					if arg_copy[1] == movement.label:
						arg_copy[1] = movement.pos - command.pos - 8
				if arg_copy[0] in self.variables:
					arg_copy[0] = self.variables[arg_copy[0]]
			if command.name == "Message":
				if arg_copy[2] in self.variables:
					arg_copy[2] = self.variables[arg_copy[2]]


			for arg in arg_copy:
				ret.extend(s(arg))
		for movement in self.movements:
			for move in movement.moves:
				ret.extend(s(move.code))
				ret.extend(s(move.args))

		return bytes(ret)

	# initialize and load this object from a .txt file
	def loadText(self, text):
		pos_count = 0
		seen_delimiter = False
		parsing_cmds = True
		for line in text:
			# skip comments
			if line.startswith("#"):
				continue

			# remove whitespace
			line = line.strip()

			vals = line.split()

			# skip empty lines
			if len(vals) == 0:
				continue

			if parsing_cmds:
				if vals[0] == "ScriptDelimiter":
					# switch to parsing movements on
					# the second script delimiter seen
					if seen_delimiter:
						parsing_cmds = False
					else:
						seen_delimiter = True

				# only start counting commands after seeing the delimiter
				if seen_delimiter:
					cmd = Command(game)
					cmd.setName(vals[0])
					cmd.args = vals[1:]
					cmd.pos = pos_count

					pos_count += 2 + 2*len(cmd.args)
					self.commands.append(cmd)
				else:
					# before first ScriptDelimiter, check for variables
					if len(vals) > 1 and vals[1] == "=":
						# variable declaration
						self.variables[vals[0]] = vals[2]

			else:
				# label, make a new movement object
				if vals[0].endswith(":"):
					movement = Movement(vals[0], pos_count)
					self.movements.append(movement)
				else:
					# move, add to last movement object
					move = Move(game)
					move.setName(vals[0], int(vals[1], 16))
					self.movements[-1].moves.append(move)
					pos_count += 4


	# initialize and load this object from an extracted binary file
	# (use raw bytes, not hex code)
	def loadBytes(self, text, isFilePointer=True):
		if isFilePointer:
			data = text.read()
		else:
			data = text

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
			last_cmd = Command(game)

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

			move = Move(game)
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


def __main__():
	if len(sys.argv) <= 1:
		print("Usage: python -m pypokescript.PokeScript 6_1194")
		print("\tIf script file is specified, text will be the output")
		print("Usage: python -m pypokescript.PokeScript 6_1194.txt")
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

if __name__ == "__main__":
	__main__()
