class NARC:
    def __init__(self, data):
        # data is the content of a NARC file, read from a NDS file

        if data[:4] != "NARC":
            raise NameError("Provided data isn't a NARC file")

        self.data = data

        btaf_pos = 0x10

        # find btaf size
        btaf_size = data[btaf_pos + 4]
        entries = data[btaf_pos + 8]

        self.files = []

        # create files for every entry seen
        for x in range(entries):
            offset_pos = btaf_pos+12 + x*8
            start, end = data[offset_pos:offset_pos+8]

        gmif_pos = btaf_pos + btaf_size +
