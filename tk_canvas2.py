from tkinter import *
from tkinter import ttk
from tkcolorpicker import askcolor
  
def pick_color():
    global color
    color = askcolor()[1]
    
def mouse_press(event):
    global prev
    prev = event

def draw(event, canvas):
    global prev
    canvas.create_line(prev.x, prev.y, event.x, event.y, fill=color, width = 5)
    prev = event

def make_rectangle(event, canvas):
    global prev
    canvas.create_rectangle(prev.x, prev.y, event.x, event.y, fill=color)
    prev = event

def main():
    global color
    root = Tk()
    color='black'
    canvas = Canvas(root, width = 640, height = 480, background = 'white')
    canvas.pack()

    canvas.bind('<ButtonPress>', mouse_press)
    canvas.bind('<Double-Button-1>', lambda event: make_rectangle(event, canvas))
    canvas.bind('<B1-Motion>', lambda event: make_rectangle(event, canvas))

    button = ttk.Button(root, text='Pick color', command=pick_color)
    button.pack()
    root.mainloop
    
if __name__ == "__main__":
    main()
