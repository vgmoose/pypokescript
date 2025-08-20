# pypokescript [![Build Status](https://travis-ci.org/vgmoose/pypokescript.svg?branch=master)](https://travis-ci.org/vgmoose/pypokescript)
Convert between B2W2 script files and a high-level scripting language

For an example of the syntax of the human-readable script files generated from this program, see [this gist](https://gist.github.com/vgmoose/a12c9d6ec2a7346b464b3cdbe2b123a6).

## Setup
Install the module using distutils and setup.py
```
git clone https://github.com/vgmoose/pypokescript.git
cd pypokescript
python3 setup.py install
```

## CLI Usage

You can invoke the CLI like this on an extracted B2W2 script binary (These can be extracted from the narchive at `a/0/5/6` in B2W2\*
```
python3 -m pypokescript.PokeScript 6_123 > pokescript.txt
```
\*You can use the nds utility (see bottom of readme) to get the .narc file out of the .nds file, and then PPNFR to extract a specific script file

If you already have a .txt pokescript respresentation (perhaps exported by this program) it can be converted back into the binary format with the following command:
```
python3 -m pypokescript.PokeScript pokescript.txt > 6_123.bin
```
At which point 6_123.bin is ready to be re-injected into the .narc file, and then the .narc file into the .nds file.

## Library Usage
See the [tests](https://github.com/vgmoose/pypokescript/blob/master/tests/shadowtriad.py) for a real example of using the library

First import the library:
```
import pypokescript as ps
```

Then create a PokeScript object from, for instance, a .txt file:
```
script = ps.PokeScript("pokescript.txt")
```

You can also create it from an extracted/exported binary (will try to detect based on the input):
```
script = ps.PokeScript("6_123")
```

Once you have your script object, you can then call either `script.getText()` or `script.getBytes()` to get either the contents of the pokescript text file or the raw bytes that would need to be inserted into the game.

## Parsing .nds files
You can list files from a .nds file by invoking the script as follows:
```
python3 -m pypokescript.games.utils.nds file.nds -l
```

Extract a single file/folder from the file structure
```
python3 -m pypokescript.games.utils.nds file.nds -e /path/to/folder/or/file
```

## Running the GUI
A GUI is in development, and requires [wxPython](https://wxpython.org/pages/downloads/index.html) and [Flask](https://pypi.org/project/Flask/1.0.2/) as dependencies. To run the GUI, use the following command:
```
python3 -m pypokescript.gui.gui
```

Currently all the GUI does is list files within a user-selected NDS file. In the future, it should provide most functionality provided by the CLI.

## Decode Pokewalker sprites
A convenience script is provided based on [the research here](https://dmitry.gr/?r=05.Projects&proj=28.%20pokewalker#_TOC_12cbaa3353b95bb71369cec4a58ae87e) that can take a HG/SS .nds file, extract the NARC where the pokewalker sprites are stored, and export them as grayscale PNG images:

```
python3 decode_pokewalker.py hgss.nds
```

## Future
- Add support for more B2W2 commands/movements
- Add support for reading/writing to .narc files
- Add other games script commands/movements/support
- Make GUI prettier and more functional!
