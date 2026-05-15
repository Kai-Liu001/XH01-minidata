from pathlib import Path

REPO_DIR = Path(__file__).parent

def print_hex(bin_path, block_size=1024, block_count=10):
    with open(bin_path, "rb") as f:
        for i in range(block_count):
            line = f.read(block_size)
            print(line.hex(' ').upper())
        
if __name__ == "__main__":
    # bin_path = r'F:\code\XH01-minidata\data\dat\JH0751_XH-01_4715_02_20260313134553_20260313135629_001401.dat'
    bin_path = r'F:\code\XH01-minidata\data\dat\JMS1301_XH-01_4715_02_20260313212113_20260313213152_001406.dat'
    print_hex(bin_path)