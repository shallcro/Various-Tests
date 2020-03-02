#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser

#set up as controller
class BdplMainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.title("Indiana University Library Born-Digital Preservation Lab")
        self.iconbitmap(r'C:/BDPL/scripts/favicon.ico')
        
        #set up variables
        self.job_type = tk.StringVar()
        self.content_source = tk.StringVar()
        self.item_barcode = tk.StringVar()
        self.unit_name = tk.StringVar()
        self.shipment_date = tk.StringVar()
        self.source_device = tk.StringVar()
        self.other_device = tk.StringVar()
        self.disk525 = tk.StringVar()
        self.re_analyze = tk.BooleanVar()
        self.bdpl_failure_notification = tk.BooleanVar()
        

        '''
        Additional variables?
        
        'collection_creator' : coll_creator, 
        'collection_title' : coll_title, 
        'content_source_type' : xfer_source, 
        'bdpl_instructions' : bdpl_instructions, 
        'appraisal_notes' : appraisal_notes, 
        'label_transcription': label_transcription, 
        'technician_note': bdpl_technician_note, 
        'noteFail' : noteFail, 
        'platform' : 'bdpl_ingest'

        'source_device' : source_device, 
        'source' : source, 
        'other_device' : other_device, 
        'disk525' : disk525, 
        'mediaStatus' : mediaStatus
        're_analyze' : re_analyze
        '''
        
        #or should this be self.bdpl_notebook ?
        bdpl_notebook = ttk.Notebook(self)
        bdpl_notebook.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.tabs = {}
        
        #other tabs: bag_prep, bdpl_to_mco, RipstationIngest
        app_tabs = {BdplIngest : 'BDPL Ingest'}
        
        for tab, description in app_tabs.items():
            tab_name = tab.__name__
            new_tab = tab(parent=bdpl_notebook, controller=self)
            bdpl_notebook.add(new_tab, text = description)
            
            self.tabs[tab_name] = new_tab
            
        self.option_add('*tearOff', False)
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        self.help_ = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.help_, label='Help')
        self.help_.add_command(label='Open BDPL wiki', command = lambda: webbrowser.open_new(r"https://wiki.dlib.indiana.edu/display/DIGIPRES/Born+Digital+Preservation+Lab"))    
        
class BdplIngest(tk.Frame):
    def __init__(self, parent, controller):

        #create main frame in notebook
        tk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.parent = parent
        self.controller = controller

        tab_frames_list = [('batch_info_frame', 'Basic Information:'), ('job_type_frame', 'Select Job Type:'), ('path_frame', 'Path to content / file list:'), ('source_device_frame', 'Select physical media or drive type:'), ('button_frame', 'BDPL Ingest Actions:'), ('bdpl_note_frame', 'Note from BDPL technician on transfer & analysis:'), ('item_metadata_frame', 'Item Metadata:')]
        
        self.tab_frames_dict = {}
        
        for name_, label_ in tab_frames_list:
            f = tk.LabelFrame(self, text = label_)
            f.pack(fill=tk.BOTH, expand=True, pady=5)
            self.tab_frames_dict[name_] = f

        '''
        BATH INFORMATION FRAME: entry fields to capture barcode, unit, and shipment date
        '''
        info = [('Item barcode:', 20, self.controller.item_barcode), ('Unit:', 5, self.controller.unit_name), ('Shipment date:', 10, self.controller.shipment_date)]
        
        for label_, width_, var_ in info:
            ttk.Label(self.tab_frames_dict['batch_info_frame'], text=label_).pack(padx=(10,0), pady=10, side=tk.LEFT)
            e = ttk.Entry(self.tab_frames_dict['batch_info_frame'], width=width_, textvariable=var_)
            e.pack(padx=10, pady=10, side=tk.LEFT)

        #set up the job type frame
        radio_buttons = [('Copy only', 'Copy_only'), ('Disk Image', 'Disk_image'), ('DVD', 'DVD'), ('CDDA', 'CDDA')]
        
        for k, v in radio_buttons:
            ttk.Radiobutton(self.tab_frames_dict['job_type_frame'], text = k, variable = self.controller.job_type, value = v, command = lambda: self.check_jobtype(self, self.controller, self.controller.job_type)).pack(side=tk.LEFT, padx=30, pady=5)

        self.re_analyze_chkbx = ttk.Checkbutton(self.tab_frames_dict['job_type_frame'], text='Rerun analysis?', variable=self.controller.re_analyze)
        self.re_analyze_chkbx.pack(side=tk.LEFT, padx=25, pady=5)
        
        '''
        PATH FRAME: entry box to display directory path and button to launch askfiledialog
        '''
        self.source_entry = ttk.Entry(self.tab_frames_dict['path_frame'], width=55, textvariable=self.controller.content_source)
        self.source_entry.pack(side=tk.LEFT, padx=(20,5), pady=5)

        self.source_button = ttk.Button(self.tab_frames_dict['path_frame'], text='Browse', command=lambda: self.source_browse(self, self.controller.content_source))
        self.source_button.pack(side=tk.LEFT, padx=(5,20), pady=5)
        
        '''
        SOURCE DEVICE FRAME: radio buttons and other widgets to record information on the source media and/or device
        '''
        devices = [('CD/DVD', '/dev/sr0'), ('3.5"', '/dev/fd0'), ('5.25"',  '5.25'), ('5.25_menu', 'menu'), ('Zip', 'Zip'), ('Other', 'Other'), ('Other_device', 'Other device name')]

        disk_type_options = ['N/A', 'Apple DOS 3.3 (16-sector)', 'Apple DOS 3.2 (13-sector)', 'Apple ProDOS', 'Commodore 1541', 'TI-99/4A 90k', 'TI-99/4A 180k', 'TI-99/4A 360k', 'Atari 810', 'MS-DOS 1200k', 'MS-DOS 360k', 'North Star MDS-A-D 175k', 'North Star MDS-A-D 350k', 'Kaypro 2 CP/M 2.2', 'Kaypro 4 CP/M 2.2', 'CalComp Vistagraphics 4500', 'PMC MicroMate', 'Tandy Color Computer Disk BASIC', 'Motorola VersaDOS']

        #loop through our devices to create radiobuttons.
        for k, v in devices:
            #Insert an option menu for 5.25" floppy disk types
            if k == '5.25_menu':
                self.controller.disk525.set('N/A')
                self.disk_menu = tk.OptionMenu(self.tab_frames_dict['source_device_frame'], self.controller.disk525, *disk_type_options)
                self.disk_menu.pack(side=tk.LEFT, padx=10, pady=5)

            #add an entry field to add POSIX name for 'other' device
            elif k == 'Other_device':
                self.controller.other_device.set('')
                ttk.Label(self.tab_frames_dict['source_device_frame'], text="(& name)").pack(side=tk.LEFT, pady=5)
                self.other_deviceEntry = tk.Entry(self.tab_frames_dict['source_device_frame'], width=5, textvariable=self.controller.other_device)
                self.other_deviceEntry.pack(side=tk.LEFT, padx=(0,10), pady=5)

            #otherwise, create radio buttons
            else:
                ttk.Radiobutton(self.tab_frames_dict['source_device_frame'], text=k, value=v, variable=self.controller.source_device).pack(side=tk.LEFT, padx=10, pady=5)
        '''
        BUTTON FRAME: buttons for BDPL Ingest actions
        '''
        button_id = {}
        buttons = ['New', 'Load', 'Transfer', 'Analyze', 'Quit']

        for b in buttons:
            button = tk.Button(self.tab_frames_dict['button_frame'], text=b, bg='light slate gray', width = 8)
            button.pack(side=tk.LEFT, padx=20, pady=5)

            button_id[b] = button

        #now use button instances to assign commands
        button_id['Load'].config(command = lambda: print(self.controller.item_barcode.get())) 

        # "New" : command= lambda: cleanUp(cleanUp_vars))
        # "Load" : command= lambda: first_run(unit.get(), unit_shipment_date.get(), barcode.get(), gui_vars))
        # "Transfer" : command= lambda: transferContent(unit.get(), unit_shipment_date.get(), barcode.get(), transfer_vars))
        # "Analyze" : command= lambda: analyzeContent(unit.get(), unit_shipment_date.get(), barcode.get(), analysis_vars))
        # "Quit" : command= lambda: closeUp(window))
        
        '''
        BDPL NOTE FRAME: text widget to record notes on the transfer/analysis process.  Also checkbox to document item failure
        '''
        self.bdpl_technician_note = tk.Text(self.tab_frames_dict['bdpl_note_frame'], height=3, width=50, wrap = 'word')
        self.bdpl_note_scroll = ttk.Scrollbar(self.tab_frames_dict['bdpl_note_frame'], orient = tk.VERTICAL, command=self.bdpl_technician_note.yview)

        self.bdpl_technician_note.config(yscrollcommand=self.bdpl_note_scroll.set)
        
        self.bdpl_technician_note.grid(row=0, column=0, padx=(10, 0), pady=10)
        self.bdpl_note_scroll.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky='ns')
        
        ttk.Button(self.tab_frames_dict['bdpl_note_frame'], text="Save", width=5, command= lambda: print(self.bdpl_technician_note.get(1.0, END))).grid(row=0, column=2, padx=10)
        
        self.controller.bdpl_failure_notification.set(False)
        
        ttk.Checkbutton(self.tab_frames_dict['bdpl_note_frame'], text="Record failed transfer with note", variable=self.controller.bdpl_failure_notification).grid(row=1, column=0, pady=(0, 10))
        
        '''
        ITEM METADATA FRAME: display info about our item to BDPL technician
        '''
        
        '''
        #pull in information from spreadsheet so tech can see what's going on
        coll_title = StringVar()
        coll_title_Label = Label(inventoryTop, text="Coll.\ntitle:")
        coll_title_Display = Label(inventoryTop, wraplength=250, justify=LEFT, textvariable=coll_title)
        coll_title_Label.grid(row=0, column=0, padx=5)
        coll_title_Display.grid(row=0, column=1, padx=5, sticky='w')
        
        coll_creator = StringVar()
        coll_creator_Label = Label(inventoryTop, text="Creator:")
        coll_creator_Display = Label(inventoryTop, wraplength=250, justify=LEFT, textvariable=coll_creator)
        coll_creator_Label.grid(row=1, column=0, padx=5)
        coll_creator_Display.grid(row=1, column=1, padx=5, sticky='w')

        xfer_source = StringVar()
        xfer_source_Label = Label(inventoryTop, text="Source:")
        xfer_source_Display = Label(inventoryTop, textvariable=xfer_source)
        xfer_source_Label.grid(row=2, column=0, padx=5)
        xfer_source_Display.grid(row=2, column=1, padx=5, sticky='w')   
        
        #some larger fields with potential for more text   
        appraisal_notes = Text(inventoryBottom, height=4, width=70)
        appraisal_scroll = Scrollbar(inventoryBottom)
        appraisal_scroll.config(command=appraisal_notes.yview)
        appraisal_notes.config(yscrollcommand=appraisal_scroll.set)
        appraisal_notes.insert(INSERT, "APPRAISAL NOTES:\n")
        appraisal_notes.grid(row=0, column=0, pady=5, padx=(5,0))
        appraisal_scroll.grid(row=0, column=1, pady=5, sticky='ns')
        appraisal_notes.configure(state='disabled')
        
        label_transcription = Text(inventoryBottom, height=4, width=70)
        label_scroll = Scrollbar(inventoryBottom)
        label_scroll.config(command=label_transcription.yview)
        label_transcription.config(yscrollcommand=label_scroll.set)
        label_transcription.insert(INSERT, "LABEL TRANSCRIPTION:\n")
        label_transcription.grid(row=1, column=0, pady=5, padx=(5,0))
        label_scroll.grid(row=1, column=1, pady=5, sticky='ns')
        #label_transcription.configure(state='disabled')
        
        bdpl_instructions = Text(inventoryBottom, height=4, width=70)
        bdpl_scroll = Scrollbar(inventoryBottom)
        bdpl_scroll.config(command=bdpl_instructions.yview)
        bdpl_instructions.config(yscrollcommand=bdpl_scroll.set)
        bdpl_instructions.insert(INSERT, "TECHNICIAN NOTES:\n")
        bdpl_instructions.grid(row=2, column=0, pady=5, padx=(5,0))
        bdpl_scroll.grid(row=2, column=1, pady=5, sticky='ns')
        bdpl_instructions.configure(state='disabled')
        
        '''
        
        

    def source_browse(self, parent, content_source):

        currdir = "Z:\\"
        selected_dir = filedialog.askdirectory(parent=parent, initialdir=currdir, title='Please select the source directory')

        if len(selected_dir) > 0:
            content_source.set(selected_dir)

    def check_jobtype(self, parent, controller, job_type):

        self.parent = parent
        self.controller = controller

        #if copy-only job, make sure source entry is enabled
        if self.controller.job_type.get()=='Copy_only':
            self.source_entry['state'] = '!disabled'
            
            self.controller.source_device.set(None)
        
        #for any other job type, hide the path frame and make sure only 1 source device frame is displayed
        else:
            self.source_entry['state'] = 'disabled'
            
            #set default source buttons for optical disks
            if self.controller.job_type.get() in ['DVD', 'CDDA']:
                self.controller.source_device.set('/dev/sr0')
            else:
                self.controller.source_device.set(None)


        
if __name__ == "__main__":

    bdpl = BdplMainApp()
    bdpl.mainloop()
    
    