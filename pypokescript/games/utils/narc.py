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

        # create files for every entry seen
        for x in range(entries):
            offset_pos = btaf_pos+12 + x*8
            start = ri(data, offset_pos)
            end = ri(data, offset_pos+4)

        offset = btaf_pos + btaf_size

        # offset by bntf size (first word in bntf header after magic)
        offset += ri(data, offset + 4) + 4

        # offset should now be pointing at the first byte in gmif header after magic
        print(offset, "%x" % data[offset])
