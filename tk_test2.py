from tkinter import Tk, Label, Button, Frame
import sys

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")
        
        # self.topFrame = Frame(self.master, width=100, height=50, bg='red')
        # self.topFrame.pack
        
        # self.middleFrame = Frame(self.master, width=100, height=50, bg='green')
        # self.middleFrame.pack
        
        # self.bottomFrame = Frame(self.master, width=100, height=50, bg='blue')
        # self.bottomFrame.pack
        

        # self.label = Label(master, text="This is our first GUI!")
        # self.label.pack()

        # self.greet_button = Button(self.topFrame, text="Greet", command=self.greet)
        # self.greet_button.pack()

        # self.close_button = Button(self.middleFrame, text="Close", command=self.quit)
        # self.close_button.pack()
        
        # self.framebutton = Button(self.bottomFrame, text="Frame", command=self.frame)
        # self.framebutton.pack()
        
        self.label = Label(master, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = Button(master, text="Greet", command=self.greet)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=self.quit)
        self.close_button.pack()
        
        self.framebutton = Button(master, text="Frame", command=self.frame)
        self.framebutton.pack()

    def greet(self):
        print("Greetings!")
    
    def quit(self):
        print('BYE!')
        sys.exit()
    
    def frame(self):
        self.test = Frame(self.master, bg="red", width=100, height=100).pack(padx=5, pady=5)
        self.label = Label(self.test, text="This is our first GUI!")
        self.label.pack()
        

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()