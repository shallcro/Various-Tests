from tkinter import *
from tkinter import ttk
from tkcolorpicker import askcolor


           

class DrawingApp:

    def __init__(self, parent):
        self.parent = parent
        
        self.canvas = Canvas(self.parent, width = 640, height = 480, background = 'white')
        self.canvas.pack()
        
        self.canvas.bind('<B1-Motion>', self.draw)
        
        self.button = ttk.Button(self.parent, text='Pick color', command=self.pick_color)
        self.button.pack()
        
        self.parent.option_add('*tearOff', False)
        self.menubar = Menu(self.parent)
        self.parent.config(menu = self.menubar)
        self.file = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.file, label='File')
        
        self.file.add_command(label='New', command = main)
        self.file.entryconfig('New', accelerator = 'Ctrl+N')
        
    
    def initial_coordinates(self, event):
        global prev
        self.prev = event
    
    def pick_color(self):
        global color
        color = askcolor()[1]
        print(color)
        
    def draw(self, event):
        self.event = event
        try:
            self.canvas.create_line(self.prev.x, self.prev.y, self.event.x, self.event.y, fill=color, width = 5)
        except AttributeError:
            pass
        self.prev = self.event
        

def main():
    global color
    color = 'black'
    root = Tk()
    DrawingApp(root)
    root.mainloop
    
if __name__ == "__main__":
    main()
