import gradio as gr

def launch_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# Trackio Dashboard\n(Placeholder UI)")
        gr.Markdown("This will show your tracked experiments.")
    demo.launch() 