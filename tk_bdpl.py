from tkinter import *
import random

class subFrame(Frame):
    def __init__(self, parent):
        super(subFrame, self).__init__()
        self.parent = parent
        self.frame_color = self.colorpicker()
        self.sub_frame = Frame(self.parent, width=650, height=50)
        self.sub_frame.pack(expand=YES, fill=BOTH)
    
    def colorpicker(self):
        # random_number = random.randint(0,16777215)
        # hex_number =format(random_number,'x')
        r = lambda: random.randint(0,255)
        return '#%02X%02X%02X' % (r(),r(),r())
        
        #return '#'+hex_number
        
    

class BDPLingest(Frame):
    def __init__(self, parent):
        self.parent = parent
        self.topFrame = Frame(self.parent, bg='white', width=650, height=250) 
        self.topFrame.pack(expand=YES, fill=BOTH)

        self.middleFrame = Frame(self.parent, bg="#000000", width=650, height=250) 
        self.middleFrame.pack(expand=YES, fill=BOTH)

        self.bottomFrame = Frame(self.parent, bg='yellow', width=650, height=250) 
        self.bottomFrame.pack(expand=YES, fill=BOTH)

        self.sub1=subFrame(self.topFrame)
        self.sub2=subFrame(self.topFrame)
        self.sub3=subFrame(self.topFrame)
        self.sub4=subFrame(self.bottomFrame)

        self.label = Label(self.sub1, text="Barcode:")
        self.label.pack(side=LEFT, padx=(10,0), pady=10)
        self.barcode = Entry(self.sub1, width=20)
        self.barcode.pack(side=RIGHT, padx=(0,10), pady=10)
       
       
       

def main():
    root = Tk()
    root.geometry('650x750')
    BDPLingest(root)
    root.mainloop()

    
if __name__ == "__main__":
    main()