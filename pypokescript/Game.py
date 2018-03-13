from .utils import *

class Game:
	def __init__(self):
		self.commands = {}
		self.moves = {}
	def postinit(self):
		doublyLink(self.commands)
		doublyLink(self.moves)