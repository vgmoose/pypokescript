# a Command is an initial command code followed by a variable
# number of arguments. The command code itself is looked up
# from the commands dict

class Command:
	def __init__(self, game):
		self.args = []
		self.arg_count = 0
		self.game = game
	def setName(self, name):
		self.name = name
		if name in self.game.commands:
			self.code = self.game.commands[name]
		else:
			try:
				self.code = int(self.name, 16)
			except:
				print("[ERROR] Unknown command: \"%s\"" % self.name)
				exit(-2)
		
	# load the name from a given code
	# also updates the number of arguments for the given code
	def setCode(self, code):
		self.code = code
		
		# if the code is a known command
		if code in self.game.commands:
			name = self.game.commands[code]
			
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