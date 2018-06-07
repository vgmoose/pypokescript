#!/bin/python3

import struct, sys, os

DUMP_DIR = "extracted"
OUTPUT_ROM = "copy.nds"

# just makes a directory without complaining
def mkdir(target):
    try:
        os.makedirs(target)
    except OSError:
        pass # already exists / error

class File(object):
    def __init__(self, id, name, nds):
        self.id = id
        self.name = name
        self.is_dir = False

        # read file size and load data into object
        size_info_pos = nds.fat_pos + 8*self.id
        start = nds.ri(size_info_pos)
        end = nds.ri(size_info_pos+4)

        self.data = nds.data[start:end]

    def __repr__(self):
        return "\"%s [%d]\"" % (self.name, self.id)

    def cache(self, parent_path, nds):
        self.path = parent_path + "/" + self.name
        nds.path_data[self.path] = self

        if self.is_dir:
            self.name = "[" + self.name + "]"   # add [] for dirs

    def extract(self):
        # print("Extracting %s to %s%s" % (self.name, DUMP_DIR, self.path))
        mkdir(os.path.dirname(DUMP_DIR + self.path))

        # create file and write bytes to it
        out = open(DUMP_DIR + self.path, "wb")
        out.write(self.data)
        out.close()

class Folder(File):
    def __init__(self, id, name, nds):
        super(Folder, self).__init__(id, name, nds)
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

class NDS(object):
    def __init__(self, path):
        self.data = None
        with open(path, "rb") as contents:
            self.data = contents.read()

        # get some basic info about the rom
        self.title = self.rs(0, 12)
        self.code = self.rs(12, 4)

        self.fnt_pos, self.fnt_len = self.ri(0x40), self.ri(0x44)
        self.fat_pos, self.fat_len = self.ri(0x48), self.ri(0x4c)

        self.rom_size = (2**17) * 2**self.rb(0x14)

        self.root = self.populate()

    # populate file data
    def populate(self):

        fnt_pos, fnt_len = self.fnt_pos, self.fnt_len
        fat_pos, fat_len = self.fat_pos, self.fat_len

        root = Folder(0, "[/]", self)
        process = []
        process.append(root)

        # map of every file to File/Folder object
        self.path_data = {"/": root}

        # as long as the folders list to process isn't empty
        while process:
            cur_dir = process.pop(0)

            cur_pos = fnt_pos + 8*(cur_dir.id & 0xfff)

            entry_start = self.ri(cur_pos)
            top_file_id = self.ri2(cur_pos+4)

            # the top file ID for this directory's files to count from
            file_id = top_file_id

            # go through entries at this cur_dir
            entry_pos = fnt_pos + entry_start

            while True:
                # flags for current entry
                flags = self.rb(entry_pos)

                name_len = flags & 0x7f
                is_dir = (flags & 0x80 != 0)

                if name_len == 0:
                    # nothing more in this cur_dir,
                    # break and move onto any next dirs to process
                    break

                # name of this folder/file
                name = self.rs(entry_pos+1, name_len)

                if is_dir:
                    # directories read their ID from disk
                    dir_id = self.ri2(entry_pos+len(name)+1) & 0xfff

                    # create a new folder entry
                    entry = Folder(dir_id, name, self)

                    # add for processing later
                    process.append(entry)

                    # move over by 2 more
                    entry_pos += 2
                else:
                    # files are given the current file_id
                    entry = File(file_id, name, self)

                # add it to the current directory
                cur_dir.add(entry)

                # cache it for lookup up by path later
                entry.cache(cur_dir.path, self)

                # increment to the next file ID
                file_id += 1

                # next entry to process
                entry_pos += len(name) + 1

        return root

    def save(self):
        # the last thing that we care about from the original rom
        banner_pos = self.ri(0x68)
        banner_len = 0x840

        # a count that keeps track of the position at the "end" of the file so far
        eof = banner_pos + banner_len

        # open up the the copy rom file (up until banner info)
        # TODO: when things seem to work reliably, replace with rewriting to the original
        out = open(OUTPUT_ROM, "wb")
        out.write(self.data[:eof])

        # we're going to try to reuse the most of the data, and only adjust
        # the data in the rom (same fnt and fat offsets and size)
        # this means no renaming or adding/removing files is possible
        # see git commit 16276bd408 for older implementation that re-used less

        # a copy of what the fat table will be to write later
        fat_table = list(self.data[self.fat_pos:self.fat_pos+self.fat_len])

        # TODO: determine the original order these filesm were in, and make sure
        # to write back in the same order

        # go through all files, grab their file ID, and write their bytes out
        process = [ self.root ]
        while process:
            node = process.pop(0)
            if node.is_dir:
                for child in node.contents:
                    if child.is_dir:
                        # folder, process children later
                        process.append(child)
                        continue

                    node_len = len(child.data)

                    # position of start, end pointers
                    start, end = eof, eof + node_len

                    # position of start/end offsets relative to fat table
                    pos = child.id * 8
                    wi(fat_table, pos, start)
                    wi(fat_table, pos+4, end)

                    # write actual data to where those offsets will be
                    out.write(child.data)

                    # update eof
                    eof += node_len

        # go back and rewrite our fat table start/end offsets over the original
        out.seek(self.fat_pos)
        out.write(bytes(fat_table))

        # finished writing
        out.close()

    def extract(self, extract_path):
        if extract_path != "/" and extract_path.endswith("/"):
            extract_path = extract_path.rstrip("/")
        # lookup entry from extraction path
        if extract_path not in self.path_data:
            print("Could not find path \"%s\" in NDS contents" % extract_path)
        else:
            entry = self.path_data[extract_path]
            mkdir(DUMP_DIR)
            # extract the files from this entry
            entry.extract()

            print("Extracted file(s) to \"./%s\" folder" % DUMP_DIR)

    # read functions (little endian)
    def ri(self, pos, size=4, type="I"):
        return int(struct.unpack("<"+type, self.data[pos:pos+size])[0])

    def ri4(self, pos):
        return self.ri(pos, 4, "I")

    def ri2(self, pos):
        return self.ri(pos, 2, "H")

    def rb(self, pos):
        return self.data[pos]

    def rs(self, pos, size):
        return self.data[pos:pos+size].decode()


# write functions (little endian)
def wi(target, pos, message, size=4, type="I"):
    write = struct.pack("<"+type, message)
    target[pos:pos+size] = write

def __main__():
    # open nds file
    parsed_args = [x for x in sys.argv if not x.startswith("-")]
    if len(parsed_args) <= 1:
        print("Please specify NDS rom file")
        print("Usage: python nds.py [-l] [-e <path_to_extract>] <file.nds>")
        print("       python nds.py -l <file.nds>")
        print("       python nds.py -e <path_to_extract> <file.nds>")
        exit(1)

    nds = None
    try:
        # try to make an nds file from it
        nds = NDS(parsed_args[1])
    except IOError:
        print("Error: Could not open file \"%s\"" % parsed_args[1])
        exit(4)

    if not nds.data:
        print("File is empty or bad permissions?")

    print("Loaded \"%s\" [%s]" % (nds.title, nds.code))
    print("ROM size: %d" % (nds.rom_size))

    print("File Name Table (FNT) info:")
    print("  offset: %d" % nds.fnt_pos)
    print("  length: %d" % nds.fnt_len)

    print("File Allocation Table (FAT) info:")
    print("  offset: %d" % nds.fat_pos)
    print("  length: %d" % nds.fat_len)

    # do argument parsing operations
    if "-l" in sys.argv:
        # print out file tree
        print("Listing file contents:")
        print(nds.root.tree())

    if "-w" in sys.argv:
        print("Creating copy of ROM at \"%s\"" % OUTPUT_ROM)

        # write out to file copy
        nds.save()

    if "-e" in sys.argv:
        arg_pos = sys.argv.index("-e") + 1
        if arg_pos >= len(sys.argv):
            print("-e requires a path to extract as an argument")
        else:
            extract_path = sys.argv[arg_pos]
            nds.extract(extract_path)

    if len(parsed_args) == len(sys.argv):
        print("No commands specified, try -l or -e <path_to_extract>")
        exit(3)

if __name__ == "__main__":
	__main__()
