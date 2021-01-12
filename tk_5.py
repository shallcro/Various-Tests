from tkinter import *

root = Tk()

def frame():
    Frame(root, bg="red", width=100, height=100).pack(padx=5, pady=5)

def window():
    Toplevel(root)

framebutton = Button(root, text="Frame", command=frame)
framewindow = Button(root, text="Window", command=window)

framebutton.pack()
framewindow.pack()

root.mainloop()