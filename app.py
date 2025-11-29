import gradio as gr
import os
from main import bot

def greet(name):
    return "Hello " + name + "!!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

bot.run(os.getenv("TOKEN"))
demo.launch()
print("hi")