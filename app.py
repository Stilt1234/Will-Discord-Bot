import gradio as gr
import os
from main import bot

def greet(name):
    bot.run(os.getenv("TOKEN"))
    return "Hello " + name + "!!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

demo.launch()
print("hi")