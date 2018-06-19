from .. import Game

class b2w2(Game.Game):

	SCRIPT_PATH = "/a/0/5/6"

	def __init__(self):
		# command : (name, arguments)
		# thanks to Kaphotics: http://pastebin.com/raw/vrkp0SN8
		self.commands = {
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

		# assume all of these take 1 argument,
		# again thanks to Kaphotics: http://pastebin.com/raw/tJXgpmYA
		self.moves = {
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

		self.postinit()
