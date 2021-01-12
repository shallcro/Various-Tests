from tkinter import *

class mainOptions:
    def __init__(self, master):
        self.master = master
        
        self.label = Label(master, text='Just a test')
        self.label.pack()
        
        self.choices = Checkbar(master, ['ingest', 'ripstation', 'bag'])
        self.choices.pack()
        
        Button(root, text='Quit', command=master.quit).pack()
        Button(root, text='Peek', command= lambda: self.allstates(choices)).pack()
        
    def allstates(self, ls): 
      print(list(ls.state()))
        
class Checkbar(Frame):
   def __init__(self, parent=None, picks=[]):
      Frame.__init__(self, parent)
      self.vars = []
      for pick in picks:
         var = IntVar()
         chk = Checkbutton(self, text=pick, variable=var)
         chk.pack()
         self.vars.append(var)
   def state(self):
      return map((lambda var: var.get()), self.vars)    






root = Tk()

main_options = mainOptions(root)

root.mainloop()

