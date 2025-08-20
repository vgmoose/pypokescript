# This script takes in a HG or SS .nds rom file, and extracts pokewalker bitmap images
# It uses DmitryGR's decodeimg script and magical's nlzss (see decodeimg.py and lzss3.py)
# Thanks to Whovian9369 for extraction assistance

import os
import sys
from pypokescript.games.utils.nds import NDS
from pypokescript.games.utils.narc import NARC
import lzss3
import decodeimg

try:
    from PIL import Image
except ImportError:
    print("PIL (Pillow) is required for image processing. Install it with: 'pip3 install Pillow'")
    sys.exit(1)

import pypokescript as ps

if len(sys.argv) < 2:
    print("Usage: python3 decode_pokewalker.py <rom.nds>")
    sys.exit(1)

# open HG or SS nds file
nds = NDS(sys.argv[1])
print(f"Opened NDS file: {sys.argv[1]}")

# open the pokewalker NARC path
narcPath = "/a/2/5/6"
narc = NARC(nds, narcPath)
print(f"Opened NARC path: {narcPath}")

# for each file, extract it, decompress it, and then decode to an image
# (assumes every width is 64 pixels)
os.makedirs("./pwalk_extracted", exist_ok=True)
print("Created directory ./pwalk_extracted for extracted files")

for idx, file in enumerate(narc.files):
    idx = f"{idx:03}"
    with open(f"./pwalk_extracted/{idx}.lzss", "wb") as f:
        f.write(file)
    print(f"Extracted file: {idx}.lzss")

    decompressed = lzss3.decompress(file)
    with open(f"./pwalk_extracted/{idx}.bin", "wb") as f:
        f.write(decompressed)
    print(f"Decompressed file: {idx}.bin")

    with open(f"./pwalk_extracted/{idx}.bin", "rb") as f:
        bytes = decodeimg.decodeimg_main(f.read(), 0, len(decompressed), 64, True)
    if bytes is not None:
        # 2-bit pixel values (0-3) to 8-bit grayscale (0-255)
        # 0=white, 1=light gray, 2=dark gray, 3=black
        pixel_map = {0: 255, 1: 170, 2: 85, 3: 0}
        mapped_bytes = [pixel_map[pixel] for pixel in bytes]
        
        # all images are 64 pixels wide
        img = Image.new("L", (64, len(bytes) // 64))
        img.putdata(mapped_bytes)
        img.save(f"./pwalk_extracted/{idx}.png")
        print(f"Saved image: {idx}.png")

print(f"Done, extracted all {len(narc.files)} pokewalker images to ./pwalk_extracted")