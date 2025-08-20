#!/usr/bin/env python3

# decodeimg - console pokewalker image decoder
# (c) 2020 DmitryGR
# GPLv3 license

# Ported from C code, original source:
# https://dmitry.gr/?r=05.Projects&proj=28.%20pokewalker#_TOC_12cbaa3353b95bb71369cec4a58ae87e

import sys
import struct

colorsFg = ["38;5;15", "38;5;253", "38;5;240", "38;5;0"]
colorsBg = ["48;5;15", "48;5;253", "48;5;240", "48;5;0"]



def escapeSeq(*seq):
    print('\x1b[', end='')
    
    for s in seq:
        if s is not None:
            print(s, end='')


def border():
    print('X', end='')


def drawImage(image, w, h):
    r = 0
    c = 0
    
    for c in range(w + 2):
        border()
    print()
    
    image_idx = 0
    for r in range(0, h, 2):
        border()

        for c in range(w):
            
            upper = image[image_idx]
            lower = 3 if r == h - 1 else image[image_idx + w]
            
            upper &= 3  # 2BPP means 2BPP
            lower &= 3
            
            if upper == lower:  # print a space with proper background color
                escapeSeq(colorsBg[upper], "m")
                print(' ', end='')
            else:  # print "upper block" with fore set to upper color and back to lower
                escapeSeq(colorsFg[upper], ";", colorsBg[lower], "m")
                
                # utf8 for upper block
                print('\u2580', end='')
            
            image_idx += 1
        
        escapeSeq("0m")  # reset
        border()
        print()
        image_idx += w
    
    for c in range(w + 2):
        border()
    print()


def usage(me):
    print(f"USAGE: {me} <offset> <num bytes> <img width> < file", file=sys.stderr)
    print("\tvalues can be hex prefixed with '0x' or decimal", file=sys.stderr)


def getInt(str_val):
    if not str_val:
        return -1
    
    if len(str_val) >= 2 and str_val[0] == '0' and str_val[1] == 'x':
        return int(str_val[2:], 16)
    else:
        return int(str_val, 10)


def decodeimg_main(input_data, ofst, nBytes, width, retBytes=False):
    # if retBytes is provided, returns the decoded bytes intsead of printing
    if ofst < 0 or nBytes < 0 or width < 0:
        raise ValueError("Arguments must be non-negative")
    
    if (nBytes % 2) or ((nBytes // 2) % width):
        raise ValueError(f"provided width {width} does not mesh with provided byte length {nBytes}")
    
    # skip start
    if len(input_data) < ofst:
        raise ValueError("input file too short for the given offset")
    
    # skip the offset bytes
    input_data = input_data[ofst:]
    
    if len(input_data) < nBytes:
        raise ValueError("input file too short for the given length")
    
    # alloc space for and read the data
    nWords = nBytes // 2
    inputData = []
    for i in range(nWords):
        if i * 2 + 1 >= len(input_data):
            raise ValueError("input file too short for the given length")
        
        c = input_data[i * 2]
        c2 = input_data[i * 2 + 1]
        inputData.append((c << 8) + c2)
    
    # alloc space for the image
    height = nWords * 8 // width
    decoded = [0] * (width * height)
    
    # decode
    inputData_idx = 0
    for r in range(0, height, 8):
        for c in range(width):
            for r2 in range(8):
                switch_val = (inputData[inputData_idx] >> r2) & 0x0101
                if switch_val == 0x000:  # white
                    decoded[(r + r2) * width + c] = 0b00
                elif switch_val == 0x001:  # dark grey
                    decoded[(r + r2) * width + c] = 0b01
                elif switch_val == 0x100:  # light grey
                    decoded[(r + r2) * width + c] = 0b10
                elif switch_val == 0x101:  # black
                    decoded[(r + r2) * width + c] = 0b11
            inputData_idx += 1
    
    if retBytes:
        return decoded
    
    print(f"image {width} x {height}", file=sys.stderr)
    drawImage(decoded, width, height)
    return 0


def og_main():
    # converts sys args into parameters for decodeimg_main
    argc = len(sys.argv)
    argv = sys.argv
    
    if argc != 4:
        usage(argv[0])
        return 1
    
    try:
        ofst = getInt(argv[1])
        nBytes = getInt(argv[2])
        width = getInt(argv[3])
    except ValueError:
        usage(argv[0])
        return 1
    
    try:
        # Read input data from stdin
        input_data = sys.stdin.buffer.read()
        
        # Call the core decoding function
        decodeimg_main(input_data, ofst, nBytes, width, retBytes=False)
        return 0
        
    except ValueError as e:
        print(str(e), file=sys.stderr)
        usage(argv[0])
        return 1


if __name__ == "__main__":
    sys.exit(og_main())
