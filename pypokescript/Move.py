# A Move is similar to a Command, however it always has one argument
# and uses a different command set (the movements dict)
# TODO:	create some base class between command/move that allows different
# 		dicts for each subclass

class Move:
	def __init__(self, game):
		self.game = game
		
	def setCode(self, code, args):
		self.code = code
		self.args = args
		
		if code in self.game.moves:
			self.name = self.game.moves[code]
		else:
			self.name = "%04x" % code
	def setName(self, name, args):
		self.name = name
		self.args = args
		
		if name in self.game.moves:
			self.code = self.game.moves[name]
		else:
			try:
				self.code = int(self.name, 16)
			except:
				print("[ERROR] Unknown movement \"%s\"" % self.name)
				exit(-3)
	
	def getText(self):
		return "%s %04x" % (self.name, self.args)