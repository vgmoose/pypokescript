import struct, sys, os

# read functions (little endian)
def ri(data, pos, size=4, type="I"):
    return int(struct.unpack("<"+type, data[pos:pos+size])[0])

def ri4(data, pos):
    return ri(data, pos, 4, "I")

class NARC:
    def __init__(self, nds, path):
        # nds is a NDS file, and path is the desired path that points to the narc file within it

        data = nds.path_data[path].data

        if data[:4].decode() != "NARC":
            raise NameError("Provided data isn't a NARC file")

        self.data = data

        btaf_pos = 0x10

        # find btaf size
        btaf_size = ri4(data, btaf_pos + 4)
        entries = ri4(data, btaf_pos + 8)

        self.files = []
        file_locs = []

        # create files for every entry seen
        for x in range(entries):
            offset_pos = btaf_pos+12 + x*8
            start = ri(data, offset_pos)
            end = ri(data, offset_pos+4)
            file_locs.append( (start, end) )

        offset = btaf_pos + btaf_size

        # offset by bntf size (first word in bntf header after magic)
        offset += ri(data, offset + 4)

        # let's make sure we're where we think we are (gmif magic)
        if data[offset:offset+4].decode() != "GMIF":
            raise NameError("While parsing NARC, couldn't find GMIF header")

        # gmif_body will now be pointing at the first byte in gmif header + 4, (after magic)
        gmif_body = offset + 8

        # the data files will be read from start, end pairings
        for loc in file_locs:
            self.files.append(data[gmif_body+loc[0]:gmif_body+loc[1]])

        # all files loaded into memory
