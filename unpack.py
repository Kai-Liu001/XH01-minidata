from pathlib import Path

REPO_DIR = Path(__file__).parent

HEADER = bytes.fromhex("1A CF FC 1D")  # 4 Bytes

input_dir = REPO_DIR / "raw"
output_dir = REPO_DIR / "data"


def unpack(file_path, save_path):
    with open(file_path, "rb") as input_file, open(save_path, "wb") as output_file:
        while True:
            line = input_file.read(1024)
            if len(line) != 1024:
                break
            assert line[:4] == HEADER
            meta = int.from_bytes(line[4:6], "big")
            # print(meta)
            VCDU = meta & 0b0000000000111111
            if VCDU != 2:#2？
                continue
            content = line[12:-130]
            output_file.write(content)


if __name__ == "__main__":
    filename = "tr_2025-11-28_16-17-33-518.dat"
    # filename = "tr_2025-10-29_17-42-58-056_02.dat"
    unpack(input_dir / filename, output_dir / filename)
