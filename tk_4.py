from tkinter import *

class Application(Frame):
    """This class creates packed frames for the GUI"""
    def __init__(self, master):
        Frame.__init__(self, master)

        # added width=180, height=40, background='red'
        self.framepack = Frame(master, width=180, height=40, background='red')
        self.framepack.pack(side=BOTTOM, fill=X)

        # added width=180, height=40, background='green'
        self.framegrid = Frame(master, width=180, height=40, background='green')
        self.framegrid.pack(side=TOP)
        self.create_widgets()

    def create_widgets(self):
        # Container 1 using LabelFrame, houses email and password labels and entries

        # Removed `self,` from the orginal code.
        self.inputlabels1 = LabelFrame(self.framepack, text="Input email login information here")
        self.inputlabels1.grid(row=0, column=0, padx=10, pady=10)        
        self.emailfield = Label(self.inputlabels1, text="Email Address")     #Labels

        # Called pack()
        self.emailfield.pack()
        self.passfield  = Label(self.inputlabels1, text="Password")

        # Called pack()
        self.passfield.pack()

root = Tk()
app = Application(root)
root.mainloop()