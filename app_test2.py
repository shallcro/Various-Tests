import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class BatchInformationFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg='red', width=650, height=50)

        ttk.Label(self, text='Item barcode:').pack(padx=(10,0), pady=10, side=tk.LEFT)
        self.item_barcode = ttk.Entry(self, width=20)
        self.item_barcode.pack(padx=10, pady=10, side=tk.LEFT)
        
        ttk.Label(self, text='Unit:').pack(padx=(10,0), pady=10, side=tk.LEFT)
        self.unit_name = ttk.Entry(self, width=5)
        self.unit_name.pack(padx=10, pady=10, side=tk.LEFT)
        
        ttk.Label(self, text='Shipment date:').pack(padx=(10,0), pady=10, side=tk.LEFT)
        self.shipmentDate = ttk.Entry(self, width=5)
        self.shipmentDate.pack(padx=10, pady=10, side=tk.LEFT)

class MainFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, height=750, width=650)
        self.pack(fill=tk.BOTH, expand=True)
        #self.pack_propagate(0)

class BDPLingestApp(tk.Frame):
    def __init__(self, parent):
        #set up variables
        #global content_source
        
        self.jobType = tk.StringVar()
        self.jobType.set(None)
        self.content_source = tk.StringVar()
        
        #create main frame in notebook
        tk.Frame.__init__(self, parent, height=750, width=650)
        self.pack(fill=tk.BOTH, expand=True)
        #self.pack_propagate(0)
        
        #set up batch information: barcode, unit, and shipment date
        self.batch_info = BatchInformationFrame(self)
        self.batch_info.pack(fill=tk.BOTH, expand=True)
        
        self.jobType_frame = tk.LabelFrame(self, text='Select Job Type:')
        self.jobType_frame.pack(fill=tk.BOTH, expand=True)
        
        
        
        self.buttons = {'Copy only' : 'Copy_only', 'Disk Image' : 'Disk_image', 'DVD' : 'DVD', 'CDDA' : 'CDDA'}
        for k, v in self.buttons.items():
            ttk.Radiobutton(self.jobType_frame, text = k, variable = self.jobType, value = v).pack(side=tk.LEFT, padx=20, pady=5)
        
        #if self.jobType.get()=='Copy_only':
        self.path_frame = tk.LabelFrame(self, text='Path to content / file list:')
        self.path_frame.pack(fill=tk.BOTH, expand=True)
        self.source_entry = ttk.Entry(self.path_frame, width=55, textvariable=self.content_source).pack(side=tk.LEFT, padx=(20,5), pady=5)
        
        self.source_button = ttk.Button(self.path_frame, text='Browse', command=lambda: self.source_browse(self, self.content_source))
        self.source_button.pack(side=tk.LEFT, padx=(5,20), pady=5)
    
    def source_browse(self, parent, content_source):
                
        currdir = "Z:\\"
        selected_dir = filedialog.askdirectory(parent=parent, initialdir=currdir, title='Please select the source directory')
        
        if len(selected_dir) > 0:
            content_source.set(selected_dir)
            print(content_source.get())
       

class RipstationIngestApp(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, height=750, width=650)
        self.pack(fill=tk.BOTH, expand=True)
        #self.pack_propagate(0)
        
        self.batch_info = BatchInformationFrame(self)
        self.batch_info.pack(fill=tk.BOTH, expand=True)
        
class NotebookApp(ttk.Notebook):
    def __init__(self, parent):
        ttk.Notebook.__init__(self, parent)
        # self.parent = parent
        
        # self.notebook = ttk.Notebook(self.parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        self.bdpl_ingest_frame = BDPLingestApp(self)
        
        self.ripstation_ingest_frame = RipstationIngestApp(self)
        
        self.add(self.bdpl_ingest_frame, text='BDPL Ingest')
        self.add(self.ripstation_ingest_frame, text='Ripstation Ingest')

        
        
        # self.button_frame = AppFrame(self.parent)
        # self.label_frame = AppFrame(self.parent)
        # self.button_frame = tk.Frame(self.parent, bg='red')
        # self.button_frame.pack(fill=tk.BOTH, expand=True)
       
        # self.label_frame = tk.Frame(self.parent, bg='blue')
        # self.label_frame.pack(fill=tk.BOTH, expand=True)
        
        
        #ttk.Button(self.parent, text='Click me', command=self.shout).pack()
        
        #ttk.Button(self.parent, text='CLICK!', command=lambda: louder('Mike')).pack()
    
    def shout(self):
        print('HEY!')

def louder(name):
    print('HHHHHHHHHHHHHHEEEEEEEEEEEEEEEEEEEEEYYYYYYYYYYYYYY {}!!!'.format(name))
        

def main():
    root = tk.Tk()
    app = NotebookApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
    