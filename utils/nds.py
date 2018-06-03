import struct

class File(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return "\"%s\"" % self.name

class Folder(File):
    def __init__(self, id, name):
        super(Folder, self).__init__(id, name)
        self.contents = []
    def add(self, file):
        self.contents.append(file)

# open nds file
data = None
with open("p.nds", "rb") as contents:
    data = contents.read()

if not data:
    print("File 'p.nds' not found")

title = data[:12]
code = data[12:16]

def ri(pos, size=4, type="I"):
    return int(struct.unpack("<"+type, data[pos:pos+size])[0])

def ri4(pos):
    return ri(pos, 4, "I")

def ri2(pos):
    return ri(pos, 2, "H")

def rb(pos):
    return ord(data[pos])

def rs(pos, size):
    return data[pos:pos+size]

fnt_pos, fnt_len = ri(0x40), ri(0x44)
fat_pos, fat_len = ri(0x48), ri(0x4c)

print("Loaded \"%s\" [%s]" % (title, code))

print("File Name Table (FNT) info:")
print("  offset: %d" % fnt_pos)
print("  length: %d" % fnt_len)

print("File Allocation Table (FAT) info:")
print("  offset: %d" % fat_pos)
print("  length: %d" % fat_len)

root = Folder(0, "/")
process = []
process.append(root)

while process:
    print process
    cur_dir = process.pop()

    cur_pos = fnt_pos + 8*(cur_dir.id & 0xFFF)

    entry_start = ri(cur_pos)
    top_file_id = ri2(cur_pos+4)

    file_id = top_file_id

    # go through entries at this cur_dir
    entry_pos = cur_pos + entry_start
    while True:
        flags = rb(entry_pos)

        name_len = flags & 0x7f
        is_dir = (flags & 0x80 != 0)

        if name_len == 0:
            # nothing more in this cur_dir,
            # break and move onto any next dirs to process
            break

        name = rs(entry_pos+1, name_len)
        print name

        if is_dir:
            entry = Folder(file_id, name)
            # add for processing later
            process.append(entry)
        else:
            entry = File(file_id, name)

        # add it to the current directory
        cur_dir.add(entry)

        # increment to the next file ID
        file_id += 1
        entry_pos += len(name) + 3    # next entry
