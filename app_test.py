import tkinter as tk
from tkinter import ttk

class AppFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

class App:
    def __init__(self, parent):
        self.parent = parent
        
        self.notebook = ttk.Notebook(self.parent)
        
        self.button_frame = AppFrame(self.parent)
        self.label_frame = AppFrame(self.parent)
        # self.button_frame = tk.Frame(self.parent, bg='red')
        # self.button_frame.pack(fill=tk.BOTH, expand=True)
       
        self.label_frame = tk.Frame(self.parent, bg='blue')
        self.label_frame.pack(fill=tk.BOTH, expand=True)
        
        jobType = tk.StringVar()
        
        self.buttons = {'Copy only' : 'Copy_only', 'Disk Image' : 'Disk_image', 'DVD' : 'DVD', 'CDDA' : 'CDDA'}
        for k, v in self.buttons.items():
            ttk.Radiobutton(self.button_frame, text = k, variable = jobType, value = v).pack(side=tk.LEFT)
        
        ttk.Label(self.label_frame, textvariable = jobType).pack()
        print(jobType.get())
        
        #ttk.Button(self.parent, text='Click me', command=self.shout).pack()
        
        #ttk.Button(self.parent, text='CLICK!', command=lambda: louder('Mike')).pack()
    
    def shout(self):
        print('HEY!')

def louder(name):
    print('HHHHHHHHHHHHHHEEEEEEEEEEEEEEEEEEEEEYYYYYYYYYYYYYY {}!!!'.format(name))
        

def main():
    root = tk.Tk()
    app = App(root)
    app.pack()
    root.mainloop()
    
if __name__ == "__main__":
    main()
    