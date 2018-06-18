from pypokescript.games.utils.nds import NDS
from pypokescript.games.utils.narc import NARC

import pypokescript as ps


nds = NDS("../POKEMON BLACK 2.nds")
narc = NARC(nds, "/a/0/5/6")

# script = ps.PokeScript(narc.files[1194], False)
#
# print(script.getText())


a = open("ex.bin", "wb")
a.write(narc.files[1194])
a.close()

print(ps.PokeScript("./ex.bin").getText())
