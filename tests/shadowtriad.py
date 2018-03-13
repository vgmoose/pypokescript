import pypokescript as ps

import hashlib

# known checksum of valid .bin that should be generated
checksum = "d3eba76925eabf9370c86b717df30d74"

# open the shadowtriad.txt file into a PokeScript object
# TODO: don't hardcode b2w2
script = ps.PokeScript("shadowtriad.txt")

# hash the bytes and ensure it matches the known checksum
m = hashlib.md5()
m.update(script.getBytes())

# TEST: does reading of .txt file generate proper binary
assert m.hexdigest()==checksum, "Checksum didn't match, invalid binary was generated from known good script"

# write that data out to a file
data = script.getBytes()
output = open("shadowtriad.bin", "wb")
output.write(data)
output.flush()

# load it into another script file
script2 = ps.PokeScript("shadowtriad.bin")

# TEST: as a sanity check, ensure the checksum from the loaded bin is still matching
m2 = hashlib.md5()
m2.update(script.getBytes())
assert m2.hexdigest()==checksum, "Checksum didn't match, invalid binary was loaded from previously generated binary"

# write it out to a txt file
output2 = open("shadowtriad_gen.txt", "w")
output2.write(script2.getText())
output2.flush()

# now we have two txt files, one we know makes a proper binary and the other is generated
# from the proper binary. So next, we'll try to load from it and hash it again

script3 = ps.PokeScript("shadowtriad_gen.txt")
m3 = hashlib.md5()
m3.update(script3.getBytes())
assert m3.hexdigest()==checksum, "Checksum didn't match, couldn't re-load from previously generated text file"