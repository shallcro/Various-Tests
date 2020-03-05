#!/usr/bin/env python3
import glob
import openpyxl
import os
import pickle
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

        self.bdpl_home_dir = bdpl_home_dir
        
        #variables entered into BDPL interface
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
        self.media_attached = tk.BooleanVar()
        self.has_transfer_list = tk.BooleanVar()

        #GUI metadata variables
        self.collection_title = tk.StringVar()
        self.collection_creator = tk.StringVar()
        self.content_source_type = tk.StringVar()
        self.item_title = tk.StringVar()
        self.label_transcription = tk.StringVar()
        self.item_description = tk.StringVar()
        self.appraisal_notes = tk.StringVar()
        self.bdpl_instructions = tk.StringVar()

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

    def get_current_tab(self):
        return self.bdpl_notebook.tab(self.bdpl_notebook.select(), 'text')
        
    def check_main_vars(self):
        if self.unit_name.get() == '':
            return (False, '\n\nERROR: please make sure you have entered a unit ID abbreviation.')

        if self.shipment_date.get() == '':
            return (False, '\n\nERROR: please make sure you have entered a shipment date.')
        
        #check barcode value, too, if we're using standard BDPL Ingest tab
        if self.get_current_tab() == 'BDPL Ingest':
            if self.item_barcode.get() == '':
                return (False, '\n\nERROR: please make sure you have entered a barcode value.')
                
        #if we get through the above, then we are good to go!
        return (True, 'Unit name and shipment date included.')

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
                ttk.Label(self.tab_frames_dict['batch_info_frame'], text=label_).pack(padx=(20,0), pady=10, side=tk.LEFT)
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
        self.source_entry = ttk.Entry(self.tab_frames_dict['path_frame'], width=60, textvariable=self.controller.path_to_content)
        self.source_entry.pack(side=tk.LEFT, padx=(20,5), pady=5)

        self.source_button = ttk.Button(self.tab_frames_dict['path_frame'], text='Browse', command=self.source_browse)
        self.source_button.pack(side=tk.LEFT, padx=(5,20), pady=5)
        
        self.controller.has_transfer_list.set(False)
        ttk.Checkbutton(self.tab_frames_dict['path_frame'], text='Transfer list?', variable=self.controller.has_transfer_list).pack(side=tk.LEFT, padx=10, pady=5)

        '''
        SOURCE DEVICE FRAME: radio buttons and other widgets to record information on the source media and/or device
        '''
        devices = [('CD/DVD', '/dev/sr0'), ('3.5"', '/dev/fd0'), ('5.25"',  '5.25'), ('5.25_menu', 'menu'), ('Zip', 'Zip'), ('Other', 'Other'), ('Other_device', 'Other device name'), ('Attached?', 'Is media attached?')]

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
            
            elif k == 'Attached?':
                self.controller.media_attached.set(False)
                ttk.Checkbutton(self.tab_frames_dict['source_device_frame'], text=k, variable=self.controller.media_attached).pack(side=tk.LEFT, padx=10, pady=5)
            #otherwise, create radio buttons
            else:
                ttk.Radiobutton(self.tab_frames_dict['source_device_frame'], text=k, value=v, variable=self.controller.source_device).pack(side=tk.LEFT, padx=10, pady=5)
                
        '''
        BUTTON FRAME: buttons for BDPL Ingest actions
        '''
        button_id = {}
        buttons = ['New', 'Load', 'Transfer', 'Analyze', 'Add PREMIS', 'Quit']

        for b in buttons:
            button = tk.Button(self.tab_frames_dict['button_frame'], text=b, bg='light slate gray', width = 10)
            button.pack(side=tk.LEFT, padx=15, pady=10)

            button_id[b] = button

        #now use button instances to assign commands
        button_id['New'].config(command = self.clear_gui)
        button_id['Load'].config(command = lambda: self.launch_session(self.controller))
        #button_id['Transfer'].config(command = lambda: )
        #button_id['Analyze'].config(command = lambda: )
        button_id['Add PREMIS']['state'] = 'disabled'
        button_id['Quit'].config(command = lambda: close_app(self.controller))


        '''
        BDPL NOTE FRAME: text widget to record notes on the transfer/analysis process.  Also checkbox to document item failure
        '''
        self.bdpl_technician_note = tk.Text(self.tab_frames_dict['bdpl_note_frame'], height=2, width=60, wrap = 'word')
        self.bdpl_note_scroll = ttk.Scrollbar(self.tab_frames_dict['bdpl_note_frame'], orient = tk.VERTICAL, command=self.bdpl_technician_note.yview)

        self.bdpl_technician_note.config(yscrollcommand=self.bdpl_note_scroll.set)

        self.bdpl_technician_note.grid(row=0, column=0, padx=(30, 0), pady=10)
        self.bdpl_note_scroll.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky='ns')

        ttk.Button(self.tab_frames_dict['bdpl_note_frame'], text="Save", width=5, command= lambda: print(self.bdpl_technician_note.get(1.0, END))).grid(row=0, column=2, padx=10)

        self.controller.bdpl_failure_notification.set(False)

        ttk.Checkbutton(self.tab_frames_dict['bdpl_note_frame'], text="Record failed transfer with note", variable=self.controller.bdpl_failure_notification).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10))

        '''
        ITEM METADATA FRAME: display info about our item to BDPL technician
        '''
        metadata_details = [('Content source:', self.controller.content_source_type), ('Collection title:', self.controller.collection_title), ('Creator:', self.controller.collection_creator), ('Item title:', self.controller.item_title), ('Label transcription', self.controller.label_transcription), ('Item description:', self.controller.item_description), ('Appraisal notes:', self.controller.appraisal_notes), ('Instructions for BDPL:', self.controller.bdpl_instructions)]
        
        c = 0
        for label_, var in metadata_details:
            l1 = tk.Label(self.tab_frames_dict['item_metadata_frame'], text=label_, anchor='e', justify=tk.RIGHT, width=18)
            l1.grid(row = c, column=0, padx=(0,5), pady=5)
            l2 = tk.Label(self.tab_frames_dict['item_metadata_frame'], textvariable=var, anchor='w', justify=tk.LEFT, width=60, wraplength=500)
            l2.grid(row = c, column=1, padx=5, pady=5)
            c+=1

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

        newscreen()
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #Standard BDPL Ingest item-based workflow
        if self.controller.get_current_tab() == 'BDPL Ingest':

            #create a barcode object and a spreadsheet object
            current_barcode_item = ItemBarcode(self.controller)
            current_spreadsheet = Spreadsheet(self.controller)

            #verify spreadsheet--make sure we only have 1 & that it follows naming conventions
            status, msg = current_spreadsheet.verify_spreadsheet()
            print(msg)
            if not status:
                del current_barcode_item, current_spreadsheet
                return

            #make sure spreadsheet is not open
            if current_spreadsheet.already_open():
                print('\n\nWARNING: {} is currently open.  Close file before continuing and/or contact digital preservation librarian if other users are involved.'.format(current_spreadsheet.spreadsheet))
                del current_barcode_item, current_spreadsheet
                return
                
            #open spreadsheet and make sure current item exists in spreadsheet; if not, return
            current_spreadsheet.open_wb()
            status, row = current_spreadsheet.return_inventory_row()
            if not status:
                print('\n\nWARNING: barcode was not found in spreadsheet.  Make sure value is entered correctly and/or check spreadsheet for value.  Consult with digital preservation librarian as needed.')
                del current_barcode_item, current_spreadsheet
                return
            
            #load metadata into item object
            current_barcode_item.load_item_metadata(current_spreadsheet, row)
            
            #assign variables to GUI
            self.controller.content_source_type.set(current_barcode_item.metadata_dict['content_source_type'])
            self.controller.collection_title.set(current_barcode_item.metadata_dict['collection_title'])
            self.controller.collection_creator.set(current_barcode_item.metadata_dict['collection_creator'])
            self.controller.item_title.set(current_barcode_item.metadata_dict.get('item_title', '-'))
            self.controller.label_transcription.set(current_barcode_item.metadata_dict['label_transcription'])
            self.controller.item_description.set(current_barcode_item.metadata_dict.get('item_description', '-'))
            self.controller.appraisal_notes.set(current_barcode_item.metadata_dict['appraisal_notes'])
            self.controller.bdpl_instructions.set(current_barcode_item.metadata_dict['bdpl_instructions'])
            
            #create folders
            current_barcode_item.create_folders()
            
            print('\n\nRecord loaded successfully; ready for next operation.')
    
    def launch_transfer(self, controller):
        self.controller = controller
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #create a barcode object and job object
        current_barcode_item = ItemBarcode(self.controller)
        current_job = IngestJob(self.controller, current_barcode_item)
        
        if current_job.job_type == 'Copy_only':
            pass
        
        #make sure we have already initiated a session for this barcode
        if not os.path.exists(current_barcode_item.barcode_dir):
            print('\n\nWARNING: load record before proceeding')
            return
    
    def clear_gui(self):
        #self.controller = controller
        
        newscreen()
        #reset all text fields/labels        
        self.controller.content_source_type.set('')
        self.controller.collection_title.set('')
        self.controller.collection_creator.set('')
        self.controller.item_title.set('')
        self.controller.label_transcription.set('')
        self.controller.item_description.set('')
        self.controller.appraisal_notes.set('')
        self.controller.bdpl_instructions.set('')
        self.controller.item_barcode.set('')
        self.controller.path_to_content.set('')
        self.controller.other_device.set('')
        
        #reset 5.25" floppy disk type
        self.controller.disk525.set('N/A')
        
        #reset checkbuttons
        self.controller.bdpl_failure_notification.set(False)
        self.controller.re_analyze.set(False)
        self.controller.media_attached.set(False)
        self.controller.has_transfer_list.set(False)
        
        #reset radio buttons
        self.controller.job_type.set(None)
        self.controller.source_device.set(None)
        
        #reset note text box
        self.bdpl_technician_note.delete('1.0', tk.END)

class Unit:
    def __init__(self, controller):
        self.controller = controller
        self.unit_name = self.controller.unit_name.get()
        self.unit_home = os.path.join(self.controller.bdpl_home_dir, self.unit_name)
        self.ingest_dir = os.path.join(self.unit_home, 'ingest')
        self.media_image_dir = os.path.join(self.controller.bdpl_home_dir, 'media-images', self.unit_name)

class Shipment(Unit):
    def __init__(self, controller):
        Unit.__init__(self, controller)
        self.controller = controller
        self.shipment_date = self.controller.shipment_date.get()
        self.ship_dir = os.path.join(self.ingest_dir, self.shipment_date)
        self.spreadsheet = os.path.join(self.ship_dir, '{}_{}.xlsx'.format(self.unit_name, self.shipment_date))

    def verify_spreadsheet(self):
        #check what is in the shipment dir
        found = glob.glob(os.path.join(self.ship_dir, '*.xlsx'))

        if len(found) == 0:
            return (False, '\nWARNING: No .XLSX spreadsheet found in {}. Check {} dropbox or consult with digital preservation librarian.'.format(self.ship_dir, self.unit_name))

        elif len(found) > 1:
            if self.spreadsheet in found:
                found.remove(self.spreadsheet)
                return (True, '\nNOTE: In addition to the shipment manifest, {} contains the following spreadsheet(s):\n\n\t{}'.format(self.ship_dir, '\n\t'.join(found)))
            else:
                return (False, '\nWARNING: the following spreadsheets do not meet the BDPL naming convention of {}_{}.xlsx:\n\n\t{}'.format(self.unit_name, self.shipment_date, '\n\t'.join(found)))

        elif found[0] == self.spreadsheet:
            return (True, '\nSpreadsheet identified.')
            
        else:
            return (False, '\n\tWARNING: {} only contains the following spreadsheet: {}'.format(self.ship_dir, found[0]))

class ItemBarcode(Shipment):
    def __init__(self, controller):
        Shipment.__init__(self, controller)
        self.controller = controller
        self.item_barcode = self.controller.item_barcode.get()
        
        self.path_to_content = self.controller.path_to_content.get().replace('/', '\\')   
        if self.controller.has_transfer_list.get():
            self.path_to_content = os.path.join(self.path_to_content, '{}.txt'.format(self.item_barcode))

        #set up main folders
        self.barcode_dir = os.path.join(self.ship_dir, self.item_barcode)
        self.image_dir = os.path.join(self.barcode_dir, "disk-image")
        self.files_dir = os.path.join(self.barcode_dir, "files")
        self.metadata_dir = os.path.join(self.barcode_dir, "metadata")
        self.temp_dir = os.path.join(self.barcode_dir, "temp")
        self.reports_dir = os.path.join(self.metadata_dir, "reports")
        self.log_dir = os.path.join(self.metadata_dir, "logs")
        self.bulkext_dir = os.path.join(self.barcode_dir, "bulk_extractor")
       
        self.folders = [self.barcode_dir, self.image_dir, self.files_dir, self.metadata_dir, self.temp_dir, self.reports_dir, self.log_dir, self.bulkext_dir, self.media_image_dir]

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
        self.ffmpeg_temp_dir = os.path.join(self.temp_dir, 'ffmpeg')
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
        
    def load_item_metadata(self, current_spreadsheet, item_row):
        
        self.metadata_dict = self.pickle_load('dict', 'metadata_dict')
        
        #if dict is empty, get info from Inventory spreadsheet
        if len(self.metadata_dict) == 0:
            #get info from inventory sheet
            ws_columns = current_spreadsheet.get_spreadsheet_columns(current_spreadsheet.inv_ws)
            
            for key in ws_columns.keys():
                if key == 'item_barcode':
                    self.metadata_dict['item_barcode'] = self.item_barcode
                else:
                    self.metadata_dict[key] = current_spreadsheet.inv_ws.cell(row=item_row, column=ws_columns[key]).value

        #now check if we need to update with any info from appraisal worksheet
        status, row = current_spreadsheet.return_appraisal_row()        
        if status:
            ws_columns = current_spreadsheet.get_spreadsheet_columns(current_spreadsheet.app_ws)
        
            for key in ws_columns.keys():
                if key == 'item_barcode':
                    self.metadata_dict['item_barcode'] = self.item_barcode
                else:
                    self.metadata_dict[key] = current_spreadsheet.app_ws.cell(row=row, column=ws_columns[key]).value
        
        #clean up any None values
        for val in self.metadata_dict:
            if self.metadata_dict[val] is None:
                self.metadata_dict[val] = '-'
        
        #save a copy so we can access later
        self.pickle_dump('metadata_dict', self.metadata_dict)
        
    def create_folders(self):
        #folders-created file will help us check for completion
        folders_created = os.path.join(self.temp_dir, 'folders_created.txt')
    
        #if file doesn't exist, create folders
        if not os.path.exists(folders_created):
            for target in self.folders:
                try:
                    os.makedirs(target)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
            
            #create file at end of loop
            open(folders_created, 'a').close()
            
    def pickle_load(self, array_type, array_name):
        
        temp_file = os.path.join(self.temp_dir, '{}.txt'.format(array_name))
        
        if array_type == 'ls':
            temp_array = []
        elif array_type == 'dict':
            temp_array = {}
        
        #make sure there's something in the file
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            with open(temp_file, 'rb') as file:
                temp_array = pickle.load(file)
                        
        return temp_array

    def pickle_dump(self, array_name, array_instance):
        
        temp_file = os.path.join(self.temp_dir, '{}.txt'.format(array_name))
         
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        with open(temp_file, 'wb') as file:
            pickle.dump(array_instance, file)
    
    def store_premis(self):
        '''
        THIS NEEDS HELP!!!
        '''
        if array_name == "premis_list":
            
            premis_path = os.path.join(metadata, '%s-premis.xml' % item_barcode)
            premis_xml_included = os.path.join(temp_dir, 'premis_xml_included.txt')
            
            #for our list of premis events, we want to pull in information that may have already been written to premis xml
            if os.path.exists(premis_path):
                
                #check to see if operation has already been completed (we'll write an empty file once we've done so)
                if not os.path.exists(premis_xml_included):
                    PREMIS_NAMESPACE = "http://www.loc.gov/premis/v3"
                    NSMAP = {'premis' : PREMIS_NAMESPACE, "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
                    parser = etree.XMLParser(remove_blank_text=True)
                    tree = etree.parse(premis_path, parser=parser)
                    root = tree.getroot()
                    events = tree.xpath("//premis:event", namespaces=NSMAP)
                    
                    for e in events:
                        temp_dict = {}
                        temp_dict['eventType'] = e.findtext('./premis:eventType', namespaces=NSMAP)
                        temp_dict['eventOutcomeDetail'] = e.findtext('./premis:eventOutcomeInformation/premis:eventOutcome', namespaces=NSMAP)
                        temp_dict['timestamp'] = e.findtext('./premis:eventDateTime', namespaces=NSMAP)
                        temp_dict['eventDetailInfo'] = e.findall('./premis:eventDetailInformation/premis:eventDetail', namespaces=NSMAP)[0].text
                        temp_dict['eventDetailInfo_additional'] = e.findall('./premis:eventDetailInformation/premis:eventDetail', namespaces=NSMAP)[1].text
                        temp_dict['linkingAgentIDvalue'] = e.findall('./premis:linkingAgentIdentifier/premis:linkingAgentIdentifierValue', namespaces=NSMAP)[1].text
                        temp_premis.append(temp_dict)
                        
                    #now create our premis_xml_included.txt file so we don't go through this again.
                    open(premis_xml_included, 'a').close()
                    
                    #if anything was added from our premix.xml file, 
        if len(temp_premis) > 0:
            for d in temp_premis:
                if not d in temp_array:
                    temp_array.append(d)
            
            #now sort based on ['timestamp']
            temp_array.sort(key=lambda x:x['timestamp'])
                
        return temp_array
        
    #def launch_transfer(self, controller):
        '''
        item_barcode
        accession_number
        collection_title
        collection_id
        collection_creator
        phys_loc
        content_source_type
        label_transcription
        appraisal_notes
        bdpl_instructions
        restriction_statement
        restriction_end_date
        initial_appraisal
        transfer_method
        migration_date
        migration_outcome
        technician_note
        extent_normal
        extent_raw
        item_file_count
        item_duplicate_count
        item_unidentified_count
        format_overview
        begin_date
        end_date
        virus_scan_results
        pii_scan_results
        full_report
        transfer_link
        final_appraisal
        '''
        
class Spreadsheet(Shipment):
    def __init__(self, controller):
        Shipment.__init__(self, controller)
        
        self.controller = controller        
        self.barcode_target = self.controller.item_barcode.get()
    
    def open_wb(self):
        self.wb = openpyxl.load_workbook(self.spreadsheet)
        self.inv_ws = self.wb['Inventory']
        self.app_ws = self.wb['Appraisal']
        self.info_ws = self.wb['Basic_Transfer_Information']
    
    def already_open(self):
        temp_file = os.path.join(os.path.dirname(self.spreadsheet), '~${}'.format(os.path.basename(self.spreadsheet)))
        if os.path.isfile(temp_file):
            return True
        else:
            return False
    
    def return_inventory_row(self):
        #set initial Boolean value to false; change to True if barcode is found
        found = False
        row = ''
        
        #if barcode exists in spreadsheet, set variable to that row
        for cell in self.inv_ws['A']:
            if (cell.value is not None):
                if self.barcode_target == str(cell.value).strip():
                    row = cell.row
                    found = True
                    break
        return found, row
    
    def return_appraisal_row(self):
        #Initially set row to next open one; if barcode is found, return its existing row
        found = False
        row = self.app_ws.max_row+1

        for cell in self.app_ws['A']:
            if (cell.value is not None):
                if self.barcode_target == str(cell.value).strip():
                    row = cell.row
                    found = True
                    break   
        return found, row    
    
    def get_spreadsheet_columns(self, ws):

        spreadsheet_columns = {}
        
        for cell in ws[1]:
            if not cell.value is None:
                if 'identifier' in str(cell.value).lower():
                    spreadsheet_columns['item_barcode'] = cell.column
                elif 'accession' in cell.value.lower():
                    spreadsheet_columns['accession_number'] = cell.column
                elif 'collection title' in cell.value.lower():
                    spreadsheet_columns['collection_title'] = cell.column
                elif 'collection id' in cell.value.lower():
                    spreadsheet_columns['collection_id'] = cell.column
                elif 'creator' in cell.value.lower():
                    spreadsheet_columns['collection_creator'] = cell.column
                elif 'physical location' in cell.value.lower():
                    spreadsheet_columns['phys_loc'] = cell.column
                elif 'source type' in cell.value.lower():
                    spreadsheet_columns['content_source_type'] = cell.column
                elif cell.value.strip().lower() == 'title':
                    spreadsheet_columns['item_title'] = cell.column
                elif 'label transcription' in cell.value.lower():
                    spreadsheet_columns['label_transcription'] = cell.column
                elif cell.value.strip().lower() == 'description':
                    spreadsheet_columns['item_description'] = cell.column
                elif 'initial appraisal notes' in cell.value.lower():
                    spreadsheet_columns['appraisal_notes'] = cell.column
                elif 'content date range' in cell.value.lower():
                    spreadsheet_columns['assigned_dates'] = cell.column
                elif 'instructions' in cell.value.lower():
                    spreadsheet_columns['bdpl_instructions'] = cell.column
                elif 'restriction statement' in cell.value.lower():
                    spreadsheet_columns['restriction_statement'] = cell.column
                elif 'restriction end date' in cell.value.lower():
                    spreadsheet_columns['restriction_end_date'] = cell.column
                elif 'move directly to sda' in cell.value.lower():
                    spreadsheet_columns['initial_appraisal'] = cell.column
                elif 'transfer method' in cell.value.lower():
                    spreadsheet_columns['transfer_method'] = cell.column
                elif 'migration date' in cell.value.lower():
                    spreadsheet_columns['migration_date'] = cell.column
                elif 'migration notes' in cell.value.lower():
                    spreadsheet_columns['technician_note'] = cell.column
                elif 'migration outcome' in cell.value.lower():
                    spreadsheet_columns['migration_outcome'] = cell.column
                elif 'extent (normalized)' in cell.value.lower():
                    spreadsheet_columns['extent_normal'] = cell.column
                elif 'extent (raw)' in cell.value.lower():
                    spreadsheet_columns['extent_raw'] = cell.column
                elif 'no. of files' in cell.value.lower():
                    spreadsheet_columns['item_file_count'] = cell.column
                elif 'no. of duplicate files' in cell.value.lower():
                    spreadsheet_columns['item_duplicate_count'] = cell.column
                elif 'no. of unidentified files' in cell.value.lower():
                    spreadsheet_columns['item_unidentified_count'] = cell.column
                elif 'file formats' in cell.value.lower():
                    spreadsheet_columns['format_overview'] = cell.column
                elif 'begin date' in cell.value.lower():
                    spreadsheet_columns['begin_date'] = cell.column
                elif 'end date' in cell.value.lower():
                    spreadsheet_columns['end_date'] = cell.column
                elif 'virus status' in cell.value.lower():
                    spreadsheet_columns['virus_scan_results'] = cell.column
                elif 'pii status' in cell.value.lower():
                    spreadsheet_columns['pii_scan_results'] = cell.column
                elif 'full report' in cell.value.lower():
                    spreadsheet_columns['full_report'] = cell.column
                elif 'link to transfer' in cell.value.lower():
                    spreadsheet_columns['transfer_link'] = cell.column
                elif 'appraisal results' in cell.value.lower():
                    spreadsheet_columns['final_appraisal'] = cell.column
                elif 'job type' in cell.value.lower():
                    spreadsheet_columns['job_type'] = cell.column
        
        return spreadsheet_columns
        
class IngestJob:
    def __init__(self, controller, current_barcode_item):
        self.controller = controller
        self.job_type = self.controller.job_type.get()
        
        if self.job_type == 'Copy_only':
        
            #make sure correct slashes are used in path
            self.path_to_content = self.controller.path_to_content.get().replace('/', '\\')
            
            if self.controller.has_transfer_list.get():
                self.path_to_content = os.path.join(self.path_to_content, '{}.txt'.format(current_barcode_item.item_barcode))
            
        

        

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
    bdpl_home_dir = 'Z:/'

    #create and launch our main app.
    bdpl = BdplMainApp(bdpl_home_dir)
    bdpl.mainloop()

if __name__ == "__main__":
    main()
