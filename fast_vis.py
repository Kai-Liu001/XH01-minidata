import os
# 使用项目内缓存目录，避免 /tmp/gradio 权限问题
_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gradio_cache")
os.makedirs(_cache_dir, exist_ok=True)
os.environ.setdefault("GRADIO_TEMP_DIR", _cache_dir)

import gradio as gr
from pathlib import Path
from PIL import Image
import numpy as np
import time

HEADER = bytes.fromhex("BB FC FC FD")  # 4 Bytes
TAIL = bytes.fromhex("4A 5B 6C 7D")  # 4 Bytes

def refresh_files():
    all_files = "\n".join(os.listdir("data/dat"))
    return all_files

def show_range(file_name):
    file_name = file_name[:-4]
    range_infrared = len(list(Path(f"data/infrared/{file_name}").iterdir()))
    range_visible = len(list(Path(f"data/visible/{file_name}").iterdir()))
    return f"{file_name} has {range_infrared} infrared images and {range_visible} visible images"


def show_infrared(file_name, range_slider):
    file_name = file_name[:-4]
    image_names = os.listdir(f"data/infrared/{file_name}")
    image_names.sort()
    if range_slider >= len(image_names):
        range_slider = len(image_names) - 1
    image_name = image_names[range_slider]
    # read as 16 bit grayscale
    # print 1% and 99% of the image
    infrared_image = Image.open(f"data/infrared/{file_name}/{image_name}")
    print("percentiles of the image:")
    print(np.percentile(np.array(infrared_image), 1))
    print(np.percentile(np.array(infrared_image), 99))
    percentile_min = np.percentile(np.array(infrared_image), 1)
    percentile_max = np.percentile(np.array(infrared_image), 99)
    infrared_image_array = np.array(infrared_image)
    # normalize to 0-255
    # infrared_image = Image.fromarray(np.array(infrared_image).byteswap())
    infrared_image = (np.array(infrared_image) - percentile_min) / (percentile_max - percentile_min) * 255
    infrared_image = np.clip(infrared_image, 0, 255)
    infrared_image = Image.fromarray(infrared_image.astype(np.uint8))
    # first line of pixels in hex capital letters in small endian
    first_line = infrared_image_array[0, :].byteswap()
    last_line = infrared_image_array[-1, :].byteswap()
    
    hex_first_line = first_line.tobytes().hex(" ").upper()
    hex_last_line = last_line.tobytes().hex(" ").upper()
    # hex_row = 
    print(infrared_image_array.shape)
    time_stamp = first_line.tobytes()[8:20].hex(" ").upper()
    
    frame_time_start = int.from_bytes(first_line.tobytes()[8:16], byteorder="big")
    delta = int.from_bytes(first_line.tobytes()[16:20], byteorder="big")
    frame_time_stamp = frame_time_start + delta
    frame_time_start_readable = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(frame_time_stamp / 1000)
    )
    
    return infrared_image, hex_first_line, hex_last_line, time_stamp, frame_time_start_readable

with gr.Blocks() as demo:
    all_files = gr.Textbox(label="All Files", value="", lines=10, interactive=False)
    refresh_button = gr.Button("Refresh All Files")
    refresh_button.click(refresh_files, outputs=[all_files])
    
    file_name = gr.Textbox(label="File Name", value="", lines=1, interactive=True)
    available_ranges = gr.Textbox(label="Available Ranges", value="", lines=10, interactive=False)
    show_range_button = gr.Button("Show Range")
    show_range_button.click(show_range, inputs=[file_name], outputs=[available_ranges])
    
    infrared_show = gr.Image(label="Infrared Show", interactive=False)
    # 滚轮控制范围
    range_slider = gr.Slider(label="Range", value=0, minimum=0, maximum=10000, step=1, interactive=True)
    time_stamp = gr.Textbox(label="Time Stamp", value="", lines=1, interactive=False)
    frame_time_start_readable = gr.Textbox(label="Frame Time Start Readable", value="", lines=1, interactive=False)
    hex_row_first = gr.Textbox(label="Hex Row First", value="", lines=1, interactive=False)
    hex_row_last = gr.Textbox(label="Hex Row Last", value="", lines=1, interactive=False)
    show_infrared_button = gr.Button("Show Infrared")
    show_infrared_button.click(show_infrared, inputs=[file_name, range_slider], outputs=[infrared_show, hex_row_first, hex_row_last, time_stamp, frame_time_start_readable])
    
    
    


# port: 1155
# host: 127.0.0.1
demo.launch(server_name="127.0.0.1", server_port=1155)