import tkinter as tk

fields = 'Last Name', 'First Name', 'Job', 'Country'

def fetch(entries):
    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        print('%s: "%s"' % (field, text)) 

def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=field, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
    return entries

if __name__ == '__main__':
    root = tk.Tk()
    ents = makeform(root, fields)
    root.bind("<Button>", (lambda event, e=ents: fetch(e)))   
    b1 = tk.Button(root, text='Show',
                  command=(lambda e=ents: fetch(e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(root, text='Quit', command=root.quit)
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    root.mainloop()



# import tkinter as tk

# def show_entry_fields():
    # print("First Name: %s\nLast Name: %s" % (_str.get(), e2.get()))
    # e1.delete(0, tk.END)
    # e2.delete(0, tk.END)

# master = tk.Tk()
# tk.Label(master, 
         # text="First Name").grid(row=0)
# tk.Label(master, 
         # text="Last Name").grid(row=1)

# _str = tk.StringVar()

# e1 = tk.Entry(master, textvariable = _str)
# e2 = tk.Entry(master)

# e1.grid(row=0, column=1)
# e2.grid(row=1, column=1)

# tk.Button(master, 
          # text='Quit', 
          # command=master.quit).grid(row=3, 
                                    # column=0, 
                                    # sticky=tk.W, 
                                    # pady=4)
# tk.Button(master, 
          # text='Show', command=show_entry_fields).grid(row=3, 
                                                       # column=1, 
                                                       # sticky=tk.W, 
                                                       # pady=4)

# tk.mainloop()

# from tkinter import *
# class Checkbar(Frame):
   # def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
      # Frame.__init__(self, parent)
      # self.vars = []
      # for pick in picks:
         # var = IntVar()
         # chk = Checkbutton(self, text=pick, variable=var)
         # chk.pack(side=side, anchor=anchor, expand=YES)
         # self.vars.append(var)
   # def state(self):
      # return map((lambda var: var.get()), self.vars)
# if __name__ == '__main__':
   # root = Tk()
   # lng = Checkbar(root, ['Python', 'Ruby', 'Perl', 'C++'])
   # tgl = Checkbar(root, ['English','German'])
   # lng.pack(side=TOP,  fill=X)
   # tgl.pack(side=LEFT)
   # lng.config(relief=GROOVE, bd=2)

   # def allstates(): 
      # print(list(lng.state()), list(tgl.state()))
      
      # if list(lng.state())[1] == 1:
        # print('RUUUUUUUUUUUUUUUUUUUUUUUUBBBBBBBBBBBBBBBBBBBBBYYYYYYYYYYYYYYYYYYYYYYYY')
        
   # Button(root, text='Quit', command=root.quit).pack(side=RIGHT)
   # Button(root, text='Peek', command=allstates).pack(side=RIGHT)
   # root.mainloop()



# from tkinter import *
# master = Tk()

# def var_states():
   # print("male: %d,\nfemale: %d" % (var1.get(), var2.get()))

# Label(master, text="Your sex:").grid(row=0, sticky=W)
# var1 = BooleanVar()
# var1.set(True)
# Checkbutton(master, text="male", variable=var1).grid(row=1, sticky=W)
# var2 = BooleanVar()
# Checkbutton(master, text="female", variable=var2).grid(row=2, sticky=W)
# Button(master, text='Quit', command=master.quit).grid(row=3, sticky=W, pady=4)
# Button(master, text='Show', command=var_states).grid(row=4, sticky=W, pady=4)
# mainloop()


# import tkinter as tk

# root = tk.Tk()

# v = tk.IntVar()
# #v.set(1)  # initializing the choice, i.e. Python

# languages = [
    # ("Python"),
    # ("Perl"),
    # ("Java"),
    # ("C++"),
    # ("C")
# ]

# def ShowChoice():
    # print(v.get())

# tk.Label(root, 
         # text="""Choose your favourite 
# programming language:""",
         # justify = tk.LEFT,
         # padx = 20).pack()

# for val, language in enumerate(languages):
    # tk.Radiobutton(root, 
                  # text=language,
                  # indicatoron = 0,
                  # width=20,
                  # padx = 20, 
                  # variable=v, 
                  # command=ShowChoice,
                  # value=val).pack(anchor=tk.W)


# root.mainloop()

# import tkinter as tk

# counter = 0 
# def counter_label(label):
  # counter = 0
  # def foo():
    # global counter
    # counter += 1
    # label.config(text=str(counter))
    # label.after(1000, foo)
  # foo()
 
 
# root = tk.Tk()
# root.title("Counting Seconds")
# label = tk.Label(root, fg="dark green")
# label.pack()
# counter_label(label)
# button = tk.Button(root, text='Stop', width=25, command=root.destroy)
# button.pack()
# root.mainloop()

# import tkinter
# try:
    # import tkinter as tk
# except ImportError:
    # import Tkinter as tk

# class Timer:
    # def __init__(self, parent):
        # # variable storing time
        # self.seconds = 0
        # # label displaying time
        # self.label = tk.Label(parent, text="0 s", font="Arial 30", width=10)
        # self.label.pack()
        # # start the timer
        # self.label.after(4000, self.refresh_label)

    # def refresh_label(self):
        # """ refresh the content of the label every second """
        # # increment the time
        # self.seconds += 1
        # # display the new time
        # self.label.configure(text="%i s" % self.seconds)
        # # request tkinter to call self.refresh after 1s (the delay is given in ms)
        # self.label.after(10, self.refresh_label)

# if __name__ == "__main__":
    # root = tk.Tk()
    # timer = Timer(root)
    # root.mainloop()