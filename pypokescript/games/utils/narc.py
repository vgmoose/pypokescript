import struct, sys, os

# read functions (little endian)
def ri(data, pos, size=4, type="I"):
    return int(struct.unpack("<"+type, data[pos:pos+size])[0])

def ri4(data, pos):
    return ri(data, pos, 4, "I")

# write functions (little endian)
def wi(data, pos, message, size=4, type="I"):
    write = struct.pack("<"+type, message)
    data[pos:pos+size] = write

class NARC:
    def __init__(self, nds, path):
        # nds is a NDS file, and path is the desired path that points to the narc file within it

        # the layout of a narc is as follows:
        # NARC
        #   - btaf (file start, end positions)
        #   - btnf (directory structure)
        #   - gmif (actual file contents)

        data = nds.path_data[path].data

        if data[:4].decode() != "NARC":
            raise NameError("Provided data isn't a NARC file")

        self.data = data

        btaf_pos = 0x10

        # stash the btaf_pos for later
        self.btaf_pos = btaf_pos

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

        btnf_size = ri(data, offset + 4)

        # save the btnf to just spit out later
        # (actually we don't have to do this, since we'll overwrite it)
        # self.btnf_data = data[]offset:offset+btnf_size]

        # offset by btnf size (first word in btnf header after magic)
        offset += btnf_size

        # let's make sure we're where we think we are (gmif magic)
        if data[offset:offset+4].decode() != "GMIF":
            raise NameError("While parsing NARC, couldn't find GMIF header")

        # gmif_body will now be pointing at the first byte in gmif header + 4, (after magic)
        gmif_body = offset + 8

        # save for later
        self.gmif_body = gmif_body

        # the data files will be read from start, end pairings
        for loc in file_locs:
            self.files.append(data[gmif_body+loc[0]:gmif_body+loc[1]])

        # all files loaded into memory

    def save(self):
        # start at the btaf header plus size and entries (these won't change)
        offset = self.btaf_pos + 8

        new_offset = 0

        # go through our files, and write our offsets out
        # (they're going to be relative to the gmif body)
        for cur_file in range(self.files):
            wi(data, offset, new_offset)
            new_offset += len(cur_file)
            wi(data, offset+4, new_offset)

            offset += 8

        # we can leave the btnf section alone, skip to gmif
        offset = self.gmif_body

        # delete everything before the raw data gets written
        del data[self.gmif_body:]

        # just go through and write the data out for every file contiguously
        for cur_file in files:
            data.append(cur_file)

        # data should now contain the new files
