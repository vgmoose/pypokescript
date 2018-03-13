# A movement file contains a set of Moves
# it can be referenced as a lebel in a PokeScript file
# using ApplyMovement

class Movement:
	def __init__(self, label, pos):
		self.moves = []
		self.label = label.rstrip(":")
		self.pos = pos