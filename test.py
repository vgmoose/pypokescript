from pypokescript.games.utils.nds import NDS
from pypokescript.games.utils.narc import NARC

from pypokescript.games.b2w2 import b2w2

import pypokescript as ps

# open nds file
nds = NDS("../POKEMON BLACK 2.nds")

# script NARC path
narc = NARC(nds, b2w2.SCRIPT_PATH)

print(ps.PokeScript(narc.files[1194], isPath=False).getText())
