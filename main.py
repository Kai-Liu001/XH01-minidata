from unpack import unpack
from parser import main as parse
from merge import merge_infrared_visible
import os
from pathlib import Path
DIR_DAT = Path("data/dat")
DIR_BIN = Path("data/bin")
DIR_ZIP = Path("data/zip")
DIR_OUT = Path("data/out")
DIR_INFRARED = Path("data/infrared")
DIR_VISIBLE = Path("data/visible")

DIR_DAT.mkdir(exist_ok=True, parents=True)
DIR_BIN.mkdir(exist_ok=True, parents=True)
DIR_ZIP.mkdir(exist_ok=True, parents=True)
DIR_OUT.mkdir(exist_ok=True, parents=True)
DIR_INFRARED.mkdir(exist_ok=True, parents=True)
DIR_VISIBLE.mkdir(exist_ok=True, parents=True)

# exit(0)

def process_file(filename):
    print(f"processing {filename}...")
    unpack(DIR_DAT / filename.name, DIR_BIN / (filename.stem + ".bin"))
    (DIR_ZIP / filename.stem).mkdir(exist_ok=True, parents=True)
    (DIR_OUT / filename.stem).mkdir(exist_ok=True, parents=True)
    print("Unpack Done!")
    
    parse(DIR_BIN / (filename.stem + ".bin"), DIR_ZIP / filename.stem, DIR_OUT / filename.stem)
    
    (DIR_INFRARED / filename.stem).mkdir(exist_ok=True, parents=True)
    (DIR_VISIBLE / filename.stem).mkdir(exist_ok=True, parents=True)
    merge_infrared_visible(DIR_OUT / filename.stem, DIR_INFRARED / filename.stem, DIR_VISIBLE / filename.stem)
    
if __name__ == "__main__":
    filenames = list(DIR_DAT.iterdir())
    for idx, filename in enumerate(filenames):
        print(f"ID:{idx:03d} filename={filename}")
    print("--------------------------------")
    idx = int(input("Enter the ID: "))
    filename = filenames[idx]
    process_file(filename)