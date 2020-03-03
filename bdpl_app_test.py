#!/usr/bin/env python3
import glob
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser

#set up as controller
class BdplMainApp(tk.Tk):
    def __init__(self, bdpl_home_dir):
        tk.Tk.__init__(self)

        self.title("Indiana University Library Born-Digital Preservation Lab")
        self.iconbitmap(r'C:/BDPL/scripts/favicon.ico')
        self.protocol('WM_DELETE_WINDOW', lambda: close_app(self))

        #variables from BDPL interface
        self.process_type = 'BDPL Ingest'
        self.bdpl_home_dir = bdpl_home_dir
        self.job_type = tk.StringVar()
        self.path_to_content = tk.StringVar()
        self.item_barcode = tk.StringVar()
        self.unit_name = tk.StringVar()
        self.shipment_date = tk.StringVar()
        self.source_device = tk.StringVar()
        self.other_device = tk.StringVar()
        self.disk525 = tk.StringVar()
        self.re_analyze = tk.BooleanVar()
        self.bdpl_failure_notification = tk.BooleanVar()

        #variables from "inventory" spreadsheet
        self.current_accession = tk.StringVar()
        self.collection_title = tk.StringVar()
        self.collection_creator = tk.StringVar()
        self.current_coll_id = tk.StringVar()
        self.phys_loc = tk.StringVar()
        self.content_source_type = tk.StringVar()
        self.item_title = tk.StringVar()
        self.label_transcription = tk.StringVar()
        self.item_description = tk.StringVar()
        self.appraisal_notes = tk.StringVar()
        self.assigned_dates = tk.StringVar()
        self.bdpl_instructions = tk.StringVar()
        self.restriction_statement = tk.StringVar()
        self.restriction_end_date = tk.StringVar()
        self.initial_appraisal = tk.StringVar()

        #variables from 'appraisal' spreadsheet
        self.transfer_method = tk.StringVar()
        self.migration_date = tk.StringVar()
        #self.technician_note = tk.StringVar() #This should be defined by tk.Text widget...
        self.migration_outcome = tk.StringVar()
        self.extent_normal = tk.StringVar()
        self.extent_raw = tk.IntVar()
        self.item_file_count = tk.IntVar()
        self.item_duplicate_count = tk.IntVar()
        self.item_unidentified_count = tk.IntVar()
        self.format_overview = tk.StringVar()
        self.begin_date = tk.StringVar()
        self.end_date = tk.StringVar()
        self.virus_scan_results = tk.StringVar()
        self.pii_scan_results = tk.StringVar()

        #create notebook to start creating app
        self.bdpl_notebook = ttk.Notebook(self)
        self.bdpl_notebook.pack(pady=10, fill=tk.BOTH, expand=True)
        
        #update info on current tab when it's switched
        self.bdpl_notebook.bind('<<NotebookTabChanged>>', lambda evt: self.get_current_tab)
        
        self.tabs = {}

        #other tabs: bag_prep, bdpl_to_mco, RipstationIngest
        app_tabs = {BdplIngest : 'BDPL Ingest'}

        for tab, description in app_tabs.items():
            tab_name = tab.__name__
            new_tab = tab(parent=self.bdpl_notebook, controller=self)
            self.bdpl_notebook.add(new_tab, text = description)

            self.tabs[tab_name] = new_tab

        self.option_add('*tearOff', False)
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        self.help_ = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.help_, label='Help')
        self.help_.add_command(label='Open BDPL wiki', command = lambda: webbrowser.open_new(r"https://wiki.dlib.indiana.edu/display/DIGIPRES/Born+Digital+Preservation+Lab"))
        
        #update info on current tab when it's switched
        #self.process_type = self.bdpl_notebook.tab(self.bdpl_notebook.select, 'text')
        
        
    def get_current_tab(self):
        self.process_type = self.bdpl_notebook.tab(self.bdpl_notebook.select, 'text')


class BdplIngest(tk.Frame):
    def __init__(self, parent, controller):

        #create main frame in notebook
        tk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.parent = parent
        self.controller = controller

        '''
        CREATE FRAMES!
        '''
        tab_frames_list = [('batch_info_frame', 'Basic Information:'), ('job_type_frame', 'Select Job Type:'), ('path_frame', 'Path to content / file list:'), ('source_device_frame', 'Select physical media or drive type:'), ('button_frame', 'BDPL Ingest Actions:'), ('bdpl_note_frame', 'Note from BDPL technician on transfer & analysis:'), ('item_metadata_frame', 'Item Metadata:')]

        self.tab_frames_dict = {}

        for name_, label_ in tab_frames_list:
            f = tk.LabelFrame(self, text = label_)
            f.pack(fill=tk.BOTH, expand=True, pady=5)
            self.tab_frames_dict[name_] = f

        '''
        BATCH INFORMATION FRAME: includes entry fields to capture barcode, unit, and shipment date
        '''
        entry_fields = [('Item barcode:', 20, self.controller.item_barcode), ('Unit:', 5, self.controller.unit_name), ('Shipment date:', 10, self.controller.shipment_date)]

        for label_, width_, var_ in entry_fields:
            if label_ == 'Shipment date:':
                self.date_combobox = ttk.Combobox(self.tab_frames_dict['batch_info_frame'], width=20, textvariable=var_, postcommand = self.update_combobox)
                self.date_combobox.pack(padx=10, pady=10, side=tk.LEFT)
            else:
                ttk.Label(self.tab_frames_dict['batch_info_frame'], text=label_).pack(padx=(20,0), pady=10, side=tk.LEFT)
                e = ttk.Entry(self.tab_frames_dict['batch_info_frame'], width=width_, textvariable=var_)
                e.pack(padx=10, pady=10, side=tk.LEFT)

        #set up the job type frame
        radio_buttons = [('Copy only', 'Copy_only'), ('Disk Image', 'Disk_image'), ('DVD', 'DVD'), ('CDDA', 'CDDA')]

        for k, v in radio_buttons:
            ttk.Radiobutton(self.tab_frames_dict['job_type_frame'], text = k, variable = self.controller.job_type, value = v, command = self.check_jobtype).pack(side=tk.LEFT, padx=30, pady=5)

        self.re_analyze_chkbx = ttk.Checkbutton(self.tab_frames_dict['job_type_frame'], text='Rerun analysis?', variable=self.controller.re_analyze)
        self.re_analyze_chkbx.pack(side=tk.LEFT, padx=25, pady=5)

        '''
        PATH FRAME: entry box to display directory path and button to launch askfiledialog
        '''
        self.source_entry = ttk.Entry(self.tab_frames_dict['path_frame'], width=55, textvariable=self.controller.path_to_content)
        self.source_entry.pack(side=tk.LEFT, padx=(20,5), pady=5)

        self.source_button = ttk.Button(self.tab_frames_dict['path_frame'], text='Browse', command=self.source_browse)
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
        button_id['New'].config(command = lambda: print(self.controller.bdpl_notebook.tab(self.controller.bdpl_notebook.select(), 'text')))
        button_id['Load'].config(command = lambda: self.launch_session(self.controller))
        #button_id['Transfer'].config(command = lambda: )
        #button_id['Analyze'].config(command = lambda: )
        button_id['Quit'].config(command = lambda: close_app(self.controller))


        '''
        BDPL NOTE FRAME: text widget to record notes on the transfer/analysis process.  Also checkbox to document item failure
        '''
        self.bdpl_technician_note = tk.Text(self.tab_frames_dict['bdpl_note_frame'], height=3, width=50, wrap = 'word')
        self.bdpl_note_scroll = ttk.Scrollbar(self.tab_frames_dict['bdpl_note_frame'], orient = tk.VERTICAL, command=self.bdpl_technician_note.yview)

        self.bdpl_technician_note.config(yscrollcommand=self.bdpl_note_scroll.set)

        self.bdpl_technician_note.grid(row=0, column=0, padx=(30, 0), pady=10)
        self.bdpl_note_scroll.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky='ns')

        ttk.Button(self.tab_frames_dict['bdpl_note_frame'], text="Save", width=5, command= lambda: print(self.bdpl_technician_note.get(1.0, END))).grid(row=0, column=2, padx=10)

        self.controller.bdpl_failure_notification.set(False)

        ttk.Checkbutton(self.tab_frames_dict['bdpl_note_frame'], text="Record failed transfer with note", variable=self.controller.bdpl_failure_notification).grid(row=1, column=0, padx=20, pady=(0, 10))

        '''
        ITEM METADATA FRAME: display info about our item to BDPL technician
        '''
        metadata_details = [('Collection title:', self.controller.collection_title), ('Creator:', self.controller.collection_creator), ('Content source:', self.controller.content_source_type)]
        
        c = 0
        for label_, var in metadata_details:
            tk.Label(self.tab_frames_dict['item_metadata_frame'], text=label_, anchor='e', justify=tk.RIGHT, width=18).grid(row = c, column=0, padx=(0,5), pady=5)
            tk.Label(self.tab_frames_dict['item_metadata_frame'], textvariable=var).grid(row = c, column=1, padx=5, pady=5)
            c+=1
        
        metadata_text_widgets = {'appraisal_notes' : 'Appraisal notes:', 'label_transcription' : 'Label transcription:', 'bdpl_instructions' : 'Instructions for BDPL:'}
        
        self.metadata_text_dict = {}
        
        #continue to use our 'c' counter...
        for k, v in metadata_text_widgets.items():
            tk.Label(self.tab_frames_dict['item_metadata_frame'], text=v, anchor='e', justify=tk.RIGHT, width=18).grid(row = c, column=0, padx=(0,5), pady=5)
            t = tk.Text(self.tab_frames_dict['item_metadata_frame'], height=3, width=50, wrap = 'word')
            s = ttk.Scrollbar(self.tab_frames_dict['item_metadata_frame'], orient = tk.VERTICAL, command=t.yview)
            t.config(yscrollcommand=s.set)
            t.grid(row=c, column=1, padx=(5, 0), pady=5)
            s.grid(row=c, column=2, padx=(0, 5), pady=(5, 0), sticky='ns')
            c+=1
            
            self.metadata_text_dict[k] = t

    def source_browse(self):

        selected_dir = filedialog.askdirectory(parent=self.parent, initialdir=self.controller.bdpl_home_dir, title='Please select the source directory')

        if len(selected_dir) > 0:
            self.controller.path_to_content.set(selected_dir)

    def check_jobtype(self):

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
    
    def update_combobox(self):
        if self.controller.unit_name.get() == '':
            combobox_list = []
        else:
            unit_home = os.path.join(self.controller.bdpl_home_dir, self.controller.unit_name.get(), 'ingest')
            combobox_list = glob.glob1(unit_home, '*')
        
        self.date_combobox['values'] = combobox_list
        
    def launch_session(self, controller):
        self.controller = controller
        
        #verify which process we are currently running
        if self.controller.process_type == 'BDPL Ingest':
            
            #create a barcode item
            current_item = ItemBarcode(self.controller)
            
            #make sure data has been entered
            if not current_item.check_variables():
                return
            else:
                print('You did it!')
        
        #figure out
        else:
            print('Protocol for other porocedures not developed yet')

class Unit:
    def __init__(self, controller):
        self.controller = controller
        self.unit_name = self.controller.unit_name.get()
        self.unit_home = os.path.join(self.controller.bdpl_home_dir, self.unit_name)
        self.ingest_dir = os.path.join(self.unit_home, 'ingest')
        
class Shipment(Unit):
    def __init__(self, controller):
        Unit.__init__(self, controller)
        self.controller = controller
        self.shipment_date = self.controller.shipment_date.get()
        self.ship_dir = os.path.join(self.ingest_dir, self.shipment_date)
        self.spreadsheet = self.find_spreadsheet()
    
    def find_spreadsheet(self):
        spreadsheet_ = os.path.join(self.ship_dir, '{}_{}.xlsx'.format(self.unit_name, self.shipment_date))
        if os.path.exists(spreadsheet_):
            return spreadsheet_
        else:
            return None
            
class ItemBarcode(Shipment):
    def __init__(self, controller):
        Shipment.__init__(self, controller)
        self.controller = controller
        self.item_barcode = self.controller.item_barcode.get()
        
        #set up main folders
        self.barcode_dir = os.path.join(self.ship_dir, self.item_barcode)
        self.image_dir = os.path.join(self.barcode_dir, "disk-image")
        self.files_dir = os.path.join(self.barcode_dir, "files")
        self.metadata_dir = os.path.join(self.barcode_dir, "metadata")
        self.temp_dir = os.path.join(self.barcode_dir, "temp")
        self.reports_dir = os.path.join(self.metadata_dir, "reports")
        self.log_dir = os.path.join(self.metadata_dir, "logs")
        self.bulkext_dir = os.path.join(self.barcode_dir, "bulk_extractor")
        self.ffmpeg_temp_dir = os.path.join(self.temp_dir, 'ffmpeg')
        
        '''SET UP FILES'''
        #assets
        self.imagefile = os.path.join(self.image_dir, '{}.dd'.format(self.item_barcode))
        self.paranoia_out = os.path.join(self.files_dir, '{}.wav'.format(self.item_barcode))
        
        #files related to disk imaging with ddrescue and FC5025
        self.mapfile = os.path.join(self.temp_dir, '{}.map'.format(self.item_barcode))
        self.ddrescue_events1 = os.path.join(self.log_dir, 'ddrescue_events1.txt')
        self.ddrescue_events2 = os.path.join(self.log_dir, 'ddrescue_events2.txt')
        self.ddrescue_rates1 = os.path.join(self.log_dir, 'ddrescue_rates1.txt')
        self.ddrescue_rates2 = os.path.join(self.log_dir, 'ddrescue_rates2.txt')
        self.ddrescue_reads1 = os.path.join(self.log_dir, 'ddrescue_reads1.txt')
        self.ddrescue_reads2 = os.path.join(self.log_dir, 'ddrescue_reads2.txt')
        self.fc5025_log = os.path.join(self.log_dir, 'fcimage.log')
        
        #log files
        self.virus_log = os.path.join(self.log_dir, 'viruscheck-log.txt')
        self.bulkext_log = os.path.join(self.log_dir, 'bulkext-log.txt')
        self.lsdvdout = os.path.join(self.reports_dir, "{}_lsdvd.xml".format(self.item_barcode))
        self.paranoia_log = os.path.join(self.log_dir, '{}-cdparanoia.log'.format(self.item_barcode))
        
        #reports
        self.disk_info_report = os.path.join(self.reports_dir, '{}-cdrdao-diskinfo.txt'.format(self.item_barcode))
        self.paranoia_out = os.path.join(self.files_dir, '{}.wav'.format(self.item_barcode))
        self.sf_file = os.path.join(self.reports_dir, 'siegfried.csv')
        self.dup_report = os.path.join(self.reports_dir, 'duplicates.csv')
        self.disktype_output = os.path.join(self.reports_dir, 'disktype.txt')
        self.fsstat_output = os.path.join(self.reports_dir, 'fsstat.txt')
        self.ils_output = os.path.join(self.reports_dir, 'ils.txt')
        self.mmls_output = os.path.join(self.reports_dir, 'mmls.txt')
        self.tree_dest = os.path.join(self.reports_dir, 'tree.txt')
        self.new_html = os.path.join(self.reports_dir, 'report.html')
        self.formatcsv = os.path.join(self.reports_dir, 'formats.csv')
        self.assets_target = os.path.join(self.reports_dir, 'assets')
        
        #temp files
        self.siegfried_db = os.path.join(self.temp_dir, 'siegfried.sqlite')
        self.cumulative_be_report = os.path.join(self.bulkext_dir, 'cumulative.txt')
        self.lsdvd_temp = os.path.join(self.temp_dir, 'lsdvd.txt')
        self.temp_dfxml = os.path.join(self.temp_dir, 'temp_dfxml.txt')
        self.dummy_audio = os.path.join(self.temp_dir, 'added_silence.mpg')
        self.cdr_scan = os.path.join(self.temp_dir, 'cdr_scan.txt')
        self.droid_profile = os.path.join(self.temp_dir, 'droid.droid')
        self.droid_out = os.path.join(self.temp_dir, 'droid.csv')
        self.temp_html = os.path.join(self.temp_dir, 'temp.html')
        self.assets_dir = 'C:\\BDPL\\resources\\assets'
        self.done_file = os.path.join(self.temp_dir, 'done.txt')
        if self.controller.job_type.get() in ['DVD', 'CDDA']:
            self.checksums = os.path.join(self.temp_dir, 'checksums_di.txt')
        else:
            self.checksums = os.path.join(self.temp_dir, 'checksums.txt')
        
        #metadata files
        self.dfxml_output = os.path.join(self.metadata_dir, '{}-dfxml.xml'.format(self.item_barcode))
        self.premis_path = os.path.join(self.metadata_dir, '{}-premis.xml'.format(self.item_barcode))
        
    def check_variables(self):
        if self.unit_name == '':
            print('\n\nError; please make sure you have entered a unit ID abbreviation.')
            return False 
        
        if self.item_barcode == '':
            print('\n\nError; please make sure you have entered a barcode.')
            return False 
        
        if self.shipment_date == '':
            print('\n\nError; please make sure you have entered a shipment date.')
            return False
            
        #if we get through all the above, then we are good to go!
        return True

def close_app(window):        
    print('BYE!')
    window.destroy()
    sys.exit(0)

def newscreen():
    os.system('cls')
    
    fname = "C:/BDPL/scripts/bdpl.txt"
    if os.path.exists(fname):
        with open(fname, 'r') as fin:
            print(fin.read())
            print('\n')
    else:
        print('Missing ASCII art header file; download to: %s' % fname)

def main():
    #clear CMD.EXE screen and print logo
    newscreen()
    
    #assign path for 'home directory'.  Change if needed...
    bdpl_home_dir = 'Z:\\'
    
    #create and launch our main app.
    bdpl = BdplMainApp(bdpl_home_dir)
    bdpl.mainloop()

if __name__ == "__main__":
    main()