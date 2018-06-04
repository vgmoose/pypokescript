import struct, sys, os

DUMP_DIR = "extracted"

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

    def __repr__(self):
        return "\"%s [%d]\"" % (self.name, self.id)

    def cache(self, parent_path):
        self.path = parent_path + "/" + self.name
        path_data[self.path] = self

        if is_dir:
            self.name = "[" + self.name + "]"   # add [] for dirs

    def extract(self):
        print("Extracting %s to %s%s" % (self.name, DUMP_DIR, self.path))
        mkdir(os.path.dirname(self.path))

        # read file size info
        size_info_pos = fat_pos + 8*self.id
        start = ri(size_info_pos)
        end = ri(size_info_pos+4)

        # # size of file to extract
		# size = end - start

        # create file and write bytes to it
        out = open(DUMP_DIR + self.path, "wb")
        out.write(data[start:end])
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
