import struct, sys, os

DUMP_DIR = "extracted"
OUTPUT_ROM = "copy.nds"

def mkdir(target):
    try:
        os.makedirs(target)
    except OSError:
        pass # already exists / error

class File(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.is_dir = False

        # read file size and load data into object
        size_info_pos = fat_pos + 8*self.id
        start = ri(size_info_pos)
        end = ri(size_info_pos+4)

        self.data = data[start:end]

    def __repr__(self):
        return "\"%s [%d]\"" % (self.name, self.id)

    def cache(self, parent_path):
        self.path = parent_path + "/" + self.name
        path_data[self.path] = self

        if is_dir:
            self.name = "[" + self.name + "]"   # add [] for dirs

    def extract(self):
        # print("Extracting %s to %s%s" % (self.name, DUMP_DIR, self.path))
        mkdir(os.path.dirname(DUMP_DIR + self.path))

        # create file and write bytes to it
        out = open(DUMP_DIR + self.path, "wb")
        out.write(self.data)
        out.close()

class Folder(File):
    def __init__(self, id=0, name=""):
        super(Folder, self).__init__(id, name)
        self.contents = []
        self.is_dir = True
        self.path = ""

    def add(self, file):
        self.contents.append(file)

    def tree(self, indent=0):
        s = (indent*" ") + self.name + "\n"
        indent += 2
        for child in self.contents:
            # if this child is a folder, go deeper
            if child.is_dir:
                s += child.tree(indent)
            else:
                s += (indent*" ") + child.name + "\n"
        return s

    def extract(self):
        # make a local folder for this NDS folder's path
        mkdir(DUMP_DIR + self.path)

        # go through children, extract them too
        for child in self.contents:
            child.extract()

# open nds file
parsed_args = [x for x in sys.argv if not x.startswith("-")]
if len(parsed_args) <= 1:
    print("Please specify NDS rom file")
    print("Usage: python nds.py [-l] [-e <path_to_extract>] <file.nds>")
    print("       python nds.py -l <file.nds>")
    print("       python nds.py -e <path_to_extract> <file.nds>")
    exit(1)

data = None
try:
    with open(parsed_args[1], "rb") as contents:
        data = contents.read()
except IOError:
    print("Error: Could not open file \"%s\"" % parsed_args[1])
    exit(4)

if not data:
    print("File is empty or bad permissions?")

title = data[:12]
code = data[12:16]

# read functions (little endian)
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


# write functions (little endian)
def wi(pos, message, size=4, type="I"):
    write = struct.pack("<"+type, message)
    out_data[pos:pos+size] = write

def wi4(pos, message):
    wi(pos, message, 4, "I")

def wi2(pos, message):
    wi(pos, message, 2, "H")

def wb(pos, message):
    out_data[pos] = chr(message)

def ws(pos, message):
    out_data[pos:pos+len(message)] = list(message)


fnt_pos, fnt_len = ri(0x40), ri(0x44)
fat_pos, fat_len = ri(0x48), ri(0x4c)

rom_size = (2**17) * 2**rb(0x14)

print("Loaded \"%s\" [%s]" % (title, code))
print("ROM size: %d" % (rom_size))

print("File Name Table (FNT) info:")
print("  offset: %d" % fnt_pos)
print("  length: %d" % fnt_len)

print("File Allocation Table (FAT) info:")
print("  offset: %d" % fat_pos)
print("  length: %d" % fat_len)

root = Folder(0, "[/]")
process = []
process.append(root)

# map of every file to File/Folder object
path_data = {"/": root}

# as long as the folders list to process isn't empty
while process:
    cur_dir = process.pop(0)

    cur_pos = fnt_pos + 8*(cur_dir.id & 0xfff)

    entry_start = ri(cur_pos)
    top_file_id = ri2(cur_pos+4)

    # the top file ID for this directory's files to count from
    file_id = top_file_id

    # go through entries at this cur_dir
    entry_pos = fnt_pos + entry_start

    while True:
        # flags for current entry
        flags = rb(entry_pos)

        name_len = flags & 0x7f
        is_dir = (flags & 0x80 != 0)

        if name_len == 0:
            # nothing more in this cur_dir,
            # break and move onto any next dirs to process
            break

        # name of this folder/file
        name = rs(entry_pos+1, name_len)

        if is_dir:
            # directories read their ID from disk
            dir_id = ri2(entry_pos+len(name)+1) & 0xfff

            # create a new folder entry
            entry = Folder(dir_id, name)

            # add for processing later
            process.append(entry)

            # move over by 2 more
            entry_pos += 2
        else:
            # files are given the current file_id
            entry = File(file_id, name)

        # add it to the current directory
        cur_dir.add(entry)

        # cache it for lookup up by path later
        entry.cache(cur_dir.path)

        # increment to the next file ID
        file_id += 1

        # next entry to process
        entry_pos += len(name) + 1

# do argument parsing operations
if "-l" in sys.argv:
    # print out file tree
    print("Listing file contents:")
    print(root.tree())

if "-w" in sys.argv:
    print("Creating copy of ROM at \"%s\"" % OUTPUT_ROM)

    # copy data into a new place in memory
    # out_data = list(data[:fat_pos+fat_len])
    # (up until banner info)
    banner_pos = ri(0x68)
    banner_len = 0x840
    out_data = list(data[:banner_pos+banner_len])

    # # write a bunch of 0xFF after the fnt start
    # out_data += ['\xff']*(rom_size - len(out_data))

    # # create fnt table reservation space
    # # contains the offset for the start of the entry and file IDs
    # dir_count = len([x for x in path_data if path_data[x].is_dir]) - 1
    # file_count = len([x for x in path_data if not path_data[x].is_dir])
    # total_name_len = sum([len(path_data[x].name) for x in path_data])
    #
    # # the amount of space to reserve for the FNT table (goes at same fnt_pos)
    # # all names + directory flags/id + directory offsets/start file_ids + file flags + "root" folder start (6)
    # new_fnt_len = total_name_len + dir_count*2 + dir_count*8 + file_count + 6
    #
    # # write this size to the fnt_len position (fnt_pos isn't touched)
    # wi(0x44, new_fnt_len)

    # this project doesn't really care about the fnt table, so let's just use the old one
    # TOOD: recopy it over based on file structure (commented out code above)
    # moved to just use more data from the base rom above
    # out_data[fnt_len:fnt_len+fnt_pos] = data[fnt_len:fnt_len+fnt_pos]

    # # create fat table
    # # contains start and end positions of every file
    # # we need the fnt table to be fully created in order to do this,
    # # otherwise we'd have to re-adjust all those start/end offsets
    #
    # # the very top file ID is where we start the offset counting from
    # toppest_file_id = ri2(fnt_pos+4)        # 87 in pearl version
    #
    # # toppest id + number of files (results in a large gap between the "0th" ID and the toppest,
    # # but that's just how it is?)
    # total_fat_entries = toppest_file_id + file_count
    # new_fat_len = total_fat_entries * 8
    #
    # # write the fat_pos (right after fnt_pos + new fnt_len, no gaps)
    # new_fat_pos = fnt_pos + fnt_len
    # wi(0x48, new_fat_pos)
    #
    # # new fat_len
    # wi(0x4c, new_fat_len)

    # we're going to try to reuse the fat table as well, since this application
    # doesn't need to move it around, only adjust offsets

    # a count that keeps track of the position at the "end" of the file so far
    # (starts at new_fat_pos + new_fat_len)
    eof = banner_pos+banner_len

    # go through all files, grab their file ID, and write their bytes out
    for path in path_data:
        node = path_data[path]
        node_len = len(node.data)

        # position of start, end pointers
        start, end = eof, eof + node_len
        out_data += ['\xff'] * node_len

        # position of start/end offsets in fat table
        pos = fat_pos + node.id * 8
        wi(pos, start)
        wi(pos+4, end)

        # write actual data to those offsets
        out_data[start:end] = node.data

        # update eof
        eof += node_len

    # write out files
    out = open(OUTPUT_ROM, "wb")
    out.write("".join(out_data))
    out.close()

if "-e" in sys.argv:
    arg_pos = sys.argv.index("-e") + 1
    if arg_pos >= len(sys.argv):
        print("-e requires a path to extract as an argument")
    else:
        extract_path = sys.argv[arg_pos]
        if extract_path != "/" and extract_path.endswith("/"):
            extract_path = extract_path.rstrip("/")
        # lookup entry from extraction path
        if extract_path not in path_data:
            print("Could not find path \"%s\" in NDS contents" % extract_path)
        else:
            entry = path_data[extract_path]
            mkdir(DUMP_DIR)
            # extract the files from this entry
            entry.extract()

            print("Extracted file(s) to \"./%s\" folder" % DUMP_DIR)

if len(parsed_args) == len(sys.argv):
    print("No commands specified, try -l or -e <path_to_extract>")
    exit(3)
