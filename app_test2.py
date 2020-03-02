#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


'''
Following class should be a subclass of BDPLingestApp--that way it will have access to all variables...
'''

class BatchInformationFrame(tk.Frame):
    def __init__(self, parent, item_barcode, unit_name, shipmentDate):
        tk.Frame.__init__(self, parent, width=650, height=50)

        self.parent = parent

        ttk.Label(self, text='Item barcode:').pack(padx=(10,0), pady=10, side=tk.LEFT)
        self.item_barcode = self.parent.item_barcode
        self.item_barcode_entry = ttk.Entry(self, width=20, textvariable=self.item_barcode)
        self.item_barcode_entry.pack(padx=10, pady=10, side=tk.LEFT)

        ttk.Label(self, text='Unit:').pack(padx=(10,0), pady=10, side=tk.LEFT)
        self.unit_name = self.parent.unit_name
        self.unit_name_entry = ttk.Entry(self, width=5, textvariable=self.unit_name)
        self.unit_name_entry.pack(padx=10, pady=10, side=tk.LEFT)

        ttk.Label(self, text='Shipment date:').pack(padx=(10,0), pady=10, side=tk.LEFT)
        self.shipmentDate = self.parent.shipmentDate
        self.shipmentDate_entry = ttk.Entry(self, width=5, textvariable=self.shipmentDate)
        self.shipmentDate_entry.pack(padx=10, pady=10, side=tk.LEFT)
        '''
        self.shipmentDate_combobox = ttk.Combobox(topFrame, width=20, postcommand= lambda: updateCombobox(self.unit_name.get(), self.shipmentDate))
        ttk.Entry(self, width=5)
        self.shipmentDate.pack(padx=10, pady=10, side=tk.LEFT)

        self.unit_shipment_date = ttk.Combobox(topFrame, width=20, postcommand= lambda: updateCombobox(unit.get(), unit_shipment_date))
        unit_shipment_date.pack(in_=topFrame, side=LEFT, padx=(0,10), pady=10)

    def updateCombobox(unit_name, unit_shipment_date):

        if unit_name == '':
            comboList = []
        else:
            unit_home = os.path.join('Z:\\', unit_name, 'ingest')
            comboList = glob.glob1(unit_home, '*')

        unit_shipment_date['values'] = comboList
        '''

class BDPLingestApp(tk.Frame):
    def __init__(self, parent):
        #set up variables
        #global content_source

        self.jobType = tk.StringVar()
        self.jobType.set(None)
        self.content_source = tk.StringVar()
        self.item_barcode = tk.StringVar()
        self.unit_name = tk.StringVar()
        self.shipmentDate = tk.StringVar()

        #create main frame in notebook
        tk.Frame.__init__(self, parent, height=750, width=650)
        self.pack(fill=tk.BOTH, expand=True)
        #self.pack_propagate(0)

        #set up buttons to handle all major actions
        self.button_frame = tk.LabelFrame(self, text='BDPL Ingest Actions')
        self.button_frame.pack(fill=tk.BOTH, expand=True)

        button_ids = {}
        buttons = ['New', 'Load', 'Transfer', 'Analyze', 'Quit']

        for b in buttons:
            button = tk.Button(self.button_frame, text=b, bg='light slate gray', width = 8)
            button.pack(side=tk.LEFT, padx=20, pady=5)

            button_ids[b] = button

        #now use button instances to assign commands
        button_ids['Load'].config(command = lambda: louder(self.item_barcode.get())) #, self.unit_name.get(), self.shipmentDate.get()))

        # "New" : command= lambda: cleanUp(cleanUp_vars))
        # "Load" : command= lambda: first_run(unit.get(), unit_shipment_date.get(), barcode.get(), gui_vars))
        # "Transfer" : command= lambda: transferContent(unit.get(), unit_shipment_date.get(), barcode.get(), transfer_vars))
        # "Analyze" : command= lambda: analyzeContent(unit.get(), unit_shipment_date.get(), barcode.get(), analysis_vars))
        # "Quit" : command= lambda: closeUp(window))

        #set up batch information frame with fields for barcode, unit, and shipment date
        self.batch_info = BatchInformationFrame(self, self.item_barcode, self.unit_name, self.shipmentDate)
        self.batch_info.pack(fill=tk.BOTH, expand=True)

        #set up the job type frame
        self.jobType_frame = tk.LabelFrame(self, text='Select Job Type:')
        self.jobType_frame.pack(fill=tk.BOTH, expand=True)

        radio_buttons = [('Copy only', 'Copy_only'), ('Disk Image', 'Disk_image'), ('DVD', 'DVD'), ('CDDA', 'CDDA')]
        for k, v in radio_buttons:
            ttk.Radiobutton(self.jobType_frame, text = k, variable = self.jobType, value = v, command = lambda: self.check_jobtype(self, self.jobType)).pack(side=tk.LEFT, padx=25, pady=5)

        self.re_analyze = tk.BooleanVar()
        self.re_analyze.set(False)
        self.re_analyze_chkbx = ttk.Checkbutton(self.jobType_frame, text='Rerun analysis?', variable=self.re_analyze)
        self.re_analyze_chkbx.pack(side=tk.LEFT, padx=25, pady=5)

    def source_browse(self, parent, content_source):

        currdir = "Z:\\"
        selected_dir = filedialog.askdirectory(parent=parent, initialdir=currdir, title='Please select the source directory')

        if len(selected_dir) > 0:
            content_source.set(selected_dir)

    def check_jobtype(self, parent, jobType):

        self.parent = parent

        if self.jobType.get()=='Copy_only':
            #if our 'device frame' exists, remove it--not needed for a copy job
            try:
                if self.source_device_frame.winfo_ismapped():
                    self.source_device_frame.pack_forget()
            except AttributeError:
                pass

            #if the path_frame still exists, pass; otherwise, set it up
            try:
                if self.path_frame.winfo_ismapped():
                    pass
                else:
                    self.path_frame.pack(fill=tk.BOTH, expand=True)
            except AttributeError:
                self.path_frame = tk.LabelFrame(self.parent, text='Path to content / file list:')
                self.path_frame.pack(fill=tk.BOTH, expand=True)
                self.source_entry = ttk.Entry(self.path_frame, width=55, textvariable=self.content_source).pack(side=tk.LEFT, padx=(20,5), pady=5)

                self.source_button = ttk.Button(self.path_frame, text='Browse', command=lambda: self.source_browse(self, self.content_source))
                self.source_button.pack(side=tk.LEFT, padx=(5,20), pady=5)

        else:
            #remove path entry box and filedialog button if NOT a copy job
            try:
                if self.path_frame.winfo_ismapped():
                    self.path_frame.pack_forget()
            except AttributeError:
                pass

            #if 'source device frame' already exists, pass; otherwise, set it up
            try:
                if self.source_device_frame.winfo_ismapped():
                    pass
                else:
                    self.source_device_frame.pack(fill=tk.BOTH, expand=True)
            except AttributeError:
                self.sourceDevice = tk.StringVar()
                self.source_device_frame = tk.LabelFrame(self.parent, text='Select physical media or drive type:')
                self.source_device_frame.pack(fill=tk.BOTH, expand=True)

                devices = [('CD/DVD', '/dev/sr0'), ('3.5"', '/dev/fd0'), ('5.25"',  '5.25'), ('5.25_menu', 'menu'), ('Zip', 'Zip'), ('Other', 'Other'), ('Other_device', 'Other device name')]

                disk_type_options = ['N/A', 'Apple DOS 3.3 (16-sector)', 'Apple DOS 3.2 (13-sector)', 'Apple ProDOS', 'Commodore 1541', 'TI-99/4A 90k', 'TI-99/4A 180k', 'TI-99/4A 360k', 'Atari 810', 'MS-DOS 1200k', 'MS-DOS 360k', 'North Star MDS-A-D 175k', 'North Star MDS-A-D 350k', 'Kaypro 2 CP/M 2.2', 'Kaypro 4 CP/M 2.2', 'CalComp Vistagraphics 4500', 'PMC MicroMate', 'Tandy Color Computer Disk BASIC', 'Motorola VersaDOS']

                #loop through our devices to create radiobuttons.
                for k, v in devices:
                    #Insert an option menu for 5.25" floppy disk types
                    if k == '5.25_menu':
                        self.disk525 = tk.StringVar()
                        self.disk525.set('N/A')
                        self.disk_menu = tk.OptionMenu(self.source_device_frame, self.disk525, *disk_type_options)
                        self.disk_menu.pack(side=tk.LEFT, padx=10, pady=5)

                    #add an entry field to add POSIX name for 'other' device
                    elif k == 'Other_device':
                        self.other_device = tk.StringVar()
                        self.other_device.set('')
                        ttk.Label(self.source_device_frame, text="(& name)").pack(side=tk.LEFT, pady=5)
                        self.other_deviceEntry = tk.Entry(self.source_device_frame, width=5, textvariable=self.other_device)
                        self.other_deviceEntry.pack(side=tk.LEFT, padx=(0,10), pady=5)

                    #otherwise, create radio buttons
                    else:
                        ttk.Radiobutton(self.source_device_frame, text=k, value=v, variable=self.sourceDevice).pack(side=tk.LEFT, padx=10, pady=5)

            #set default source buttons for optical disks
            if self.jobType.get() in ['DVD', 'CDDA']:
                self.sourceDevice.set('/dev/sr0')
            else:
                self.sourceDevice.set(None)

class RipstationIngestApp(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent) #, height=750, width=650)
        self.pack(fill=tk.BOTH, expand=True)
        tk.Label(text='hi').pack()
        #self.pack_propagate(0)
        #
        # self.batch_info = BatchInformationFrame(self, self.item_barcode, self.unit_name, self.shipmentDate)
        # self.batch_info.pack(fill=tk.BOTH, expand=True)

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
