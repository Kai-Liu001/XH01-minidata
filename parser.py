from collections import OrderedDict
from pathlib import Path
import zipfile
from colorama import Fore, Style

# file = "tr_2025-08-21_10-51-13-560.dat"
# file = "tr_2025-08-29_10-43-24-366.dat"
# file = "tr_2025-09-15_09-53-33-603.dat"
# file = "tr_2025-10-29_17-42-58-056_02.dat"
# file = "tr_2025-11-28_16-17-33-518.dat"

work_dir = Path(__file__).parent.resolve()
# input = work_dir / "data" / file

# zipped_dir = work_dir / "zip" / input.stem
# unzip_dir = work_dir / "unzip" / input.stem
# zipped_dir.mkdir(exist_ok=True, parents=True)
# unzip_dir.mkdir(exist_ok=True, parents=True)
HEADER = bytes.fromhex("BB FC FC FD")
TAIL = bytes.fromhex("4A 5B 6C 7D")
BUFFER_SIZE = 400 * 1024 * 1024
FRAME_LEN = 10276

# total_size = input.stat().st_size
parsed_size = 0
prev_key = None

data_dict = {}
log_dict = {
    1: f"{Fore.RED}1{Style.RESET_ALL}",
    2: f"{Fore.GREEN}2{Style.RESET_ALL}",
    3: "3",
}


def find_pattern_in_binary_file(content: bytes):
    i = 0
    positions = []
    while i < len(content):
        index = content.find(HEADER, i)
        if index != -1:
            positions.append(index)
            i = index + len(HEADER)
        else:
            break
    return positions


def save_packet(prev_key, zipped_dir: Path, unzip_dir: Path):
    task_type, exec_id, packet_id, frame_total_cnt = prev_key
    frame_dict = data_dict[(task_type, exec_id, packet_id, frame_total_cnt)]
    # sourt by frame_id
    frame_dict = OrderedDict(sorted(frame_dict.items()))

    frame_id_list = list(frame_dict.keys())
    if frame_id_list[0] != 0:
        print(
            f"[{Fore.RED}Frame ID not start from 0{Style.RESET_ALL}] TaskType: {task_type}, ExecID: {exec_id}, PacketID: {packet_id}, TotalFrameCnt: {frame_total_cnt}"
        )
        return
    if len(frame_id_list) != frame_total_cnt:
        print(
            f"[{Fore.RED}Frame ID not continuous{Style.RESET_ALL}] TaskType: {task_type}, ExecID: {exec_id}, PacketID: {packet_id}, TotalFrameCnt: {frame_total_cnt}"
        )
        return
    # concatinate all frame payload
    payload = b""
    for frame_id in frame_dict:
        payload += frame_dict[frame_id]
    # save to file
    print(
        f"[{Fore.GREEN}Saved{Style.RESET_ALL}] TaskType: {task_type}, ExecID: {exec_id}, PacketID: {packet_id}, TotalFrameCnt: {frame_total_cnt}"
    )
    with open(zipped_dir / f"{task_type}_{exec_id}_{packet_id}.zip", "wb") as file:
        file.write(payload)
    # unzip it into ./unzip/
    try:
        unzip_task_dir = unzip_dir / f"{task_type}_{exec_id}_{packet_id}"
        unzip_task_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(
            zipped_dir / f"{task_type}_{exec_id}_{packet_id}.zip", "r"
        ) as zip_ref:
            zip_ref.extractall(unzip_task_dir)
    except Exception as e:
        print(
            f"[{Fore.RED}Unzip failed{Style.RESET_ALL}] Task ID: {log_dict[task_type]}, Pass ID: {exec_id}, Packet ID: {packet_id}"
        )


def parse_packet(packet: bytes, zipped_dir: Path, unzip_dir: Path):
    """
    total length <= 10276 Bytes

    Header (4B)             0:4
    TaskType (1B)           4:5
    ExecID (4B)             5:9
    PacketID (4B)           9:13
    FrameTotalCnt (4B)      13:17
    FrameID (4B)            17:21
    PayloadLen (4B)         21:25
    Payload (<=10240B)      25:25+PL
    CRC (8B)                25+PL:33+PL
    Tail (4B)               33+PL:37+PL
    """
    global prev_key
    task_type = int.from_bytes(packet[4:5], byteorder="big")
    exec_id = int.from_bytes(packet[5:9], byteorder="big")
    packet_id = int.from_bytes(packet[9:13], byteorder="big")
    frame_total_cnt = int.from_bytes(packet[13:17], byteorder="big")
    frame_id = int.from_bytes(packet[17:21], byteorder="big")
    payload_len = int.from_bytes(packet[21:25], byteorder="big")
    tail = packet[33 + payload_len : 37 + payload_len]
    if tail != TAIL:
        print(
            f"[{Fore.RED}Tail not match{Style.RESET_ALL}] TaskType: {task_type}, ExecID: {exec_id}, PacketID: {packet_id}, Frame: {frame_id}/{frame_total_cnt-1}, PL: {payload_len}"
        )
        return
    print(
        f"[{Fore.GREEN}Match{Style.RESET_ALL}] TaskType: {task_type}, ExecID: {exec_id}, PacketID: {packet_id}, Frame: {frame_id}/{frame_total_cnt-1}, PL: {payload_len}"
    )
    payload = packet[25 : 25 + payload_len]
    key = (task_type, exec_id, packet_id, frame_total_cnt)
    if prev_key and prev_key != key:
        save_packet(prev_key, zipped_dir, unzip_dir)
    prev_key = key
    if key not in data_dict:
        data_dict[key] = {}
    if frame_id not in data_dict[key]:
        data_dict[key][frame_id] = payload


def main(bin_path: Path, zipped_dir: Path, unzip_dir: Path):
    with open(bin_path, "rb") as of:
        def read_buffer() -> bytes:
            global parsed_size
            content = of.read(BUFFER_SIZE)
            if len(content) == 0:
                return None
            parsed_size += len(content)
            print(
                f"progress=[{round(parsed_size/1024**3, 3)}GB]"
            )
            if not content:
                return content
            while content[-1] in HEADER:  #
                nextB = of.read(1)
                if not nextB:
                    return content
                else:
                    content += nextB
                    parsed_size += 1
                    print(
                        f"progress=[{round(parsed_size/1024**3, 3)}GB]"
                    )
            return content

        content = read_buffer()
        while content:
            BUFFER_CUT = False
            for position in find_pattern_in_binary_file(content):
                if len(content) - position < FRAME_LEN:  # 被BUFFER截断或者文件读完了
                    more = read_buffer()
                    if more is not None:
                        # 被 buffer 截断了
                        # print(f"buffer cut, position={position}")
                        BUFFER_CUT = True
                        content = content[position:] + more
                        break
                    else:
                        # 文件读完了
                        # print(f"file end, position={position}")
                        parse_packet(content[position:], zipped_dir, unzip_dir)
                        return

                else:
                    # 正常解析
                    # print(f"normal parse, position={position}")
                    parse_packet(content[position : position + FRAME_LEN + 1], zipped_dir, unzip_dir)
            if not BUFFER_CUT:
                content = read_buffer()


if __name__ == "__main__":
    of = open(input, "rb")
    main(of)
    of.close()
