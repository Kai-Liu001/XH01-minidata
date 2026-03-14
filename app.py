import gradio as gr
import os
from main import process_file

def refresh_files():
    current_files.value = "\n".join(os.listdir("data/dat"))
    return current_files

with gr.Blocks() as demo:
    # current files in dat
    current_files = gr.Textbox(label="Current Files", value="", lines=10, interactive=False)
    # refresh button
    refresh_button = gr.Button(label="Refresh")
    # input filename
    input_filename = gr.Textbox(label="Input Filename", value="", lines=1, interactive=True)
    # process button
    process_button = gr.Button(label="Process")
    # show_file
    # name
    # infrared show
    infrared_show = gr.Image(label="Infrared Show", value="", interactive=False)
    # visible show
    visible_show = gr.Image(label="Visible Show", value="", interactive=False)
    # show button
    show_button = gr.Button(label="Show")

    refresh_button.click(refresh_files, outputs=[current_files])
    process_button.click(process_file, inputs=[input_filename])
    show_button.click(show_file, inputs=[input_filename], outputs=[infrared_show, visible_show])




refresh_button.click(refresh_files)
# port: 1155
# host: 127.0.0.1
demo.launch(server_name="127.0.0.1", server_port=1155)