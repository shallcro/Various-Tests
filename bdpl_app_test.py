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
        self.disk_525_type = tk.StringVar()
        self.re_analyze = tk.BooleanVar()
        self.bdpl_failure_notification = tk.BooleanVar()
        self.media_attached = tk.BooleanVar()

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

        '''
        SOURCE DEVICE FRAME: radio buttons and other widgets to record information on the source media and/or device
        '''
        devices = [('CD/DVD', '/dev/sr0'), ('3.5"', '/dev/fd0'), ('5.25"',  '5.25'), ('5.25_menu', 'menu'), ('Zip', 'Zip'), ('Other', 'Other'), ('Other_device', 'Other device name'), ('Attached?', 'Is media attached?')]

        disk_type_options = ['N/A', 'Apple DOS 3.3 (16-sector)', 'Apple DOS 3.2 (13-sector)', 'Apple ProDOS', 'Commodore 1541', 'TI-99/4A 90k', 'TI-99/4A 180k', 'TI-99/4A 360k', 'Atari 810', 'MS-DOS 1200k', 'MS-DOS 360k', 'North Star MDS-A-D 175k', 'North Star MDS-A-D 350k', 'Kaypro 2 CP/M 2.2', 'Kaypro 4 CP/M 2.2', 'CalComp Vistagraphics 4500', 'PMC MicroMate', 'Tandy Color Computer Disk BASIC', 'Motorola VersaDOS']

        #loop through our devices to create radiobuttons.
        for k, v in devices:
            #Insert an option menu for 5.25" floppy disk types
            if k == '5.25_menu':
                self.controller.disk_525_type.set('N/A')
                self.disk_menu = tk.OptionMenu(self.tab_frames_dict['source_device_frame'], self.controller.disk_525_type, *disk_type_options)
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

        #for any other job type, disable the path frame.  If CDDA or DVD job type, pre-select the 'CD/DVD' source device radio button
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

        #make sure we have already initiated a session for this barcode
        if not os.path.exists(current_barcode_item.barcode_dir):
            print('\n\nWARNING: load record before proceeding')
            return
        
        #Copy only job
        if current_job.job_type == 'Copy_only':
            current_job.secure_copy(current_job.path_to_content)
        
        #Disk image job type
        elif current_job.job_type == 'Disk_image':
            
            #if 5.25" floppy, use FC5025 floppy controller and associated software
            if current_job.source_device == '5.25':
                if current_job.disk_525_type == 'N/A':
                    print('\n\nWARNING: select the appropriate 5.25" floppy disk type from the drop down menu.')
                    return
                else:
                    current_job.fc5025_image()
            
            #otherwise, use ddrescue
            else:
                current_job.ddrescue_image()
                
            #get technical metadata from disk image
            current_job.disk_image_info()
            
            #replicate files from disk image
            current_job.disk_image_replication()
            
        elif current_job.job_type == 'DVD':
            #create disk image of DVD
            current_job.ddrescue_image()
            
            #check DVD for title information
            drive_letter = "{}\\".format(self.optical_drive_letter())
            titlecount, title_format = self.lsdvd_check(drive_letter)
            
            #make surre this isn't PAL formatted: need to figure out solution. 
            if title_format == 'PAL':
                print('\n\nWARNING: DVD is PAL formatted! Notify digital preservation librarian so we can configure approprioate ffmpeg command; set disc aside for now...')
                return
            
            #if DVD has one or more titles, rip raw streams to .MPG
            if titlecount > 0:
                self.normalize_dvd_content(titlecount, drive_letter)
            else:
                print('\nWARNING: DVD does not appear to have any titles; job type should likely be Disk_image.  Manually review disc and re-transfer content if necessary.')
                return
        
        elif current_job.job_type == 'CDDA':
            #create a copy or raw pulse code modulated (PCM) audio data 
            self.cdda_image_creation()
            
            #now rip CDDA to WAV using cd-paranoia (Cygwin build; note hyphen)
            self.cdda_wav_creation()
        
        else: 
            print('\n\nError; please indicate the appropriate job type')
            return
    
        print('\n\n--------------------------------------------------------------------------------------------------\n\n')
    
    def launch_analysis(self, controller):
        self.controller = controller
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #create a barcode object and job object
        current_barcode_item = ItemBarcode(self.controller)
        current_job = IngestJob(self.controller, current_barcode_item)

        #make sure we have already initiated a session for this barcode
        if not os.path.exists(current_barcode_item.barcode_dir):
            print('\n\nWARNING: load record before proceeding')
            return
            
        # if jobType not in ['Disk_image', 'Copy_only', 'DVD', 'CDDA']:
            # print('\n\nError; please indicate the appropriate job type')
            # return
        
        #copy in .CSS and .JS files for HTML report
        if os.path.exists(current_barcode_item.assets_target):
            pass
        else:
            shutil.copytree(current_barcode_item.assets_dir, current_barcode_item.assets_target)
            
        '''run antivirus'''
        print('\nVIRUS SCAN: clamscan.exe')
        if current_job.check_premis('virus check') and not current_job.re_analyze:
            print('\n\tVirus scan already completed; moving on to next step...')
        else:
            current_job.run_antivirus()
    
        '''create DFXML (if not already done so)'''
        if current_job.check_premis('message digest calculation') and not current_job.re_analyze:
            print('\n\nDIGITAL FORENSICS XML CREATION:')
            print('\n\tDFXML already created; moving on to next step...')
        else:
            if current_job.job_type == 'Disk_image':
                #DFXML creation for disk images will depend on the image's file system; check fs_list
                fs_list = pickle_load(self.barcode_item, 'ls', 'fs_list')
                
                #if it's an HFS+ file system, we can use fiwalk on the disk image; otherwise, use bdpl_ingest on the file directory
                if 'hfs+' in [fs.lower() for fs in fs_list]:
                    current_job.produce_dfxml(self.barcode_item.imagefile)
                else:
                    current_job.produce_dfxml(self.barcode_item.files_dir)
            
            elif current_job.job_type == 'Copy_only':
                current_job.produce_dfxml(self.barcode_item.files_dir)
            
            elif current_job.job_type == 'DVD':
                current_job.produce_dfxml(self.barcode_item.imagefile)
            
            elif current_job.job_type == 'CDDA':
                current_job.produce_dfxml(self.barcode_item.image_dir)
                
        '''run bulk_extractor to identify potential sensitive information (only if disk image or copy job type). Skip if b_e was run before'''
        print('\n\nSENSITIVE DATA SCAN: BULK_EXTRACTOR')
        if current_job.check_premis('sensitive data scan') and not current_job.re_analyze:
            print('\n\tSensitive data scan already completed; moving on to next step...')
        else:
            if current_job.job_type in ['Copy_only', 'Disk_image']:
                current_job.run_bulkext()
            else:
                print('\n\tSensitive data scan not required for DVD-Video or CDDA content; moving on to next step...')
                
        '''run siegfried to characterize file formats'''
        print('\n\nFILE FORMAT ANALYSIS')
        if current_job.check_premis('format identification') and not current_job.re_analyze:
            print('\n\tFile format analysis already completed; moving on to next operation...')
        else:
            current_job.format_analysis()
        
        #load siegfried.csv into sqlite database; skip if it's already completed
        if not os.path.exists(self.barcode_item.sqlite_done) or current_job.re_analyze:
            current_job.import_csv() # load csv into sqlite db
        
        '''create HTML and CSV reports'''
        current_job.stats_and_report_creation()
        
        #generate PREMIS preservation metadata file
        premis_path = os.path.join(metadata, '%s-premis.xml' % item_barcode)
        print_premis(premis_path, folders, item_barcode)
    
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
        self.controller.disk_525_type.set('N/A')
        
        #reset checkbuttons
        self.controller.bdpl_failure_notification.set(False)
        self.controller.re_analyze.set(False)
        self.controller.media_attached.set(False)
        
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
        self.mapfile = os.path.join(self.log_dir, '{}.map'.format(self.item_barcode))
        self.fc5025_log = os.path.join(self.log_dir, 'fcimage.log')

        #log files
        self.virus_log = os.path.join(self.log_dir, 'viruscheck-log.txt')
        self.bulkext_log = os.path.join(self.log_dir, 'bulkext-log.txt')
        self.lsdvd_out = os.path.join(self.reports_dir, "{}_lsdvd.xml".format(self.item_barcode))
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
        self.duplicates = os.path.join(self.temp_dir, 'duplicates.txt')
        self.folders_created = os.path.join(self.temp_dir, 'folders-created.txt')
        self.sqlite_done = os.path.join(self.temp_dir, 'sqlite_done.txt')
        self.done_file = os.path.join(self.temp_dir, 'done.txt')
        if self.controller.job_type.get() in ['DVD', 'CDDA']:
            self.checksums = os.path.join(self.temp_dir, 'checksums_di.txt')
        else:
            self.checksums = os.path.join(self.temp_dir, 'checksums.txt')

        #metadata files
        self.dfxml_output = os.path.join(self.metadata_dir, '{}-dfxml.xml'.format(self.item_barcode))
        self.premis_path = os.path.join(self.metadata_dir, '{}-premis.xml'.format(self.item_barcode))
        
    def load_item_metadata(self, current_spreadsheet, item_row):
        
        self.metadata_dict = pickle_load(self, 'dict', 'metadata_dict')
        
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
        pickle_dump(self, 'metadata_dict', self.metadata_dict)
        
    def create_folders(self):
        #folders-created file will help us check for completion

        #if file doesn't exist, create folders
        if not os.path.exists(self.folders_created):
            for target in self.folders:
                try:
                    os.makedirs(target)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
            
            #create file at end of loop
            open(self.folders_created, 'a').close()
 
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
       
        self.barcode_item = current_barcode_item
        
        self.job_type = self.controller.job_type.get()
        self.process_type = self.controller.get_current_tab()
        
        if 'bdpl_transfer_list' in self.path_to_content:
            self.path_to_content = os.path.join(self.path_to_content.replace('/', '\\'), '{}.txt'.format(self.item_barcode))
        else:
            self.path_to_content = self.controller.path_to_content.get().replace('/', '\\')
        self.source_device = self.controller.source_device.get()
        self.other_device = self.controller.other_device.get()
        self.disk_525_type = self.controller.disk_525_type.get()
        self.re_analyze = self.controller.re_analyze.get()
        self.bdpl_failure_notification = self.controller.bdpl_failure_notification.get()
        self.media_attached = self.controller.media_attached.get()
        
        self.disk_type_options = { 'Apple DOS 3.3 (16-sector)' : 'apple33', 'Apple DOS 3.2 (13-sector)' : 'apple32', 'Apple ProDOS' : 'applepro', 'Commodore 1541' : 'c1541', 'TI-99/4A 90k' : 'ti99', 'TI-99/4A 180k' : 'ti99ds180', 'TI-99/4A 360k' : 'ti99ds360', 'Atari 810' : 'atari810', 'MS-DOS 1200k' : 'msdos12', 'MS-DOS 360k' : 'msdos360', 'North Star MDS-A-D 175k' : 'mdsad', 'North Star MDS-A-D 350k' : 'mdsad350', 'Kaypro 2 CP/M 2.2' : 'kaypro2', 'Kaypro 4 CP/M 2.2' : 'kaypro4', 'CalComp Vistagraphics 4500' : 'vg4500', 'PMC MicroMate' : 'pmc', 'Tandy Color Computer Disk BASIC' : 'coco', 'Motorola VersaDOS' : 'versa' }
        
    def secure_copy(self, content_source):
        
        if not os.path.exists(content_source):
            print('\n\nFile source does not exist: "{}"\n\nPlease verify the correct source has been identified.'.format(content_source))
            return

        #function takes the file source and destination as well as  a specific premis event to be used in documenting action
        print('\n\nFILE REPLICATION: TERACOPY\n\n\tSOURCE: {} \n\tDESTINATION: {}'.format(content_source, self.barcode_item.files_dir))
        
        #set variables for premis
        timestamp = str(datetime.datetime.now())             
        migrate_ver = "TeraCopy v3.26"
        
        #set variables for copy operation; note that if we are using a file list, TERACOPY requires a '*' before the source. 
        if os.path.isfile(content_source):
            copycmd = 'TERACOPY COPY *"{}" {} /SkipAll /CLOSE'.format(content_source, self.barcode_item.files_dir)
        else:
            copycmd = 'TERACOPY COPY "{}" {} /SkipAll /CLOSE'.format(content_source, self.barcode_item.files_dir)
        
        try:
            exitcode = subprocess.call(copycmd, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            print('\n\tFile replication failed:\n\n\t{}'.format(e))
            return
                
        #need to find Teracopy SQLITE db and export list of copied files to csv log file
        list_of_files = glob.glob(os.path.join(os.path.expandvars('C:\\Users\%USERNAME%\AppData\Roaming\TeraCopy\History'), '*'))
        tera_db = max(list_of_files, key=os.path.getctime)
        
        conn = sqlite3.connect(tera_db)
        conn.text_factory = str
        cur = conn.cursor()
        results = cur.execute("SELECT * from Files")
        
        tera_log = os.path.join(self.barcode_item.log_dir, 'teracopy_log.csv')
        with open(tera_log, 'w', encoding='utf8') as output:
            writer = csv.writer(output, lineterminator='\n')
            header = ['Source', 'Offset', 'State', 'Size', 'Attributes', 'IsFolder', 'Creation', 'Access', 'Write', 'SourceCRC', 'TargetCRC', 'TargetName', 'Message', 'Marked', 'Hidden']
            writer.writerow(header)
            writer.writerows(results)

        cursor.close()
        conn.close()    
        
        #get count of files that were actually moved
        with open(tera_log, 'r', encoding='utf8') as input:
            csvreader = csv.reader(input)
            count = sum(1 for row in csvreader) - 1
        print('\n\t{} files successfully transferred to {}.'.format(count, self.barcode_item.files_dir))
        
        #record premis
        self.record_premis(timestamp, event_type, event_outcome, event_detail, event_detail_note, agent_id, self.barcode_item)       
            
        print('\n\tFile replication completed; proceed to content analysis.')

    def fc5025_image(self):
    
        print('\n\n\DISK IMAGE CREATION: DeviceSideData FC5025\n\n\tSOURCE: 5.25" floppy disk \n\tDESTINATION: %s\n\n' % self.barcode_item.imagefile)       

        timestamp = str(datetime.datetime.now())
        
        copycmd = 'fcimage -f {} {} | tee -a {}'.format(self.disk_type_options[self.disk_525_type], self.barcode_item.imagefile, self.barcode_item.fc5025_log)

        exitcode = subprocess.call(copycmd, shell=True, text=True)
        
        #NOTE: FC5025 will return non-zero exitcode if any errors detected.  As disk image creation may still be 'successful', we will fudge the results a little bit.  Failure == no disk image.
        if exitcode != 0:
            
            if os.stat(imagefile).st_size > 0:
                exitcode = 0
            
            else:
                print('\n\nWARNING: Disk image not successfully created. Verify you have selected the correct disk type and try again (if possible).  Otherwise, indicate issues in note to collecting unit.')
                return
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'disk image creation', exitcode, copycmd, 'Extracted a disk image from the physical information carrier.', 'FCIMAGE v1309', self.barcode_item)
        
        print('\n\n\tDisk image created; proceeding to next step...')
    
    def ddrescue_image(self):
    
        #for Zip disks, we need to determine the POSIX device name.  
        if self.source_device == 'Zip':
            
            #get POSIX device names from /proc/partitions
            check_device = subprocess.check_output('cat /proc/partitions', shell=True, text=True)
            
            #get all physical drives and associated drive letters using PowerShell
            ps_cmd = "Get-Partition | % {New-Object PSObject -Property @{'DiskModel'=(Get-Disk $_.DiskNumber).Model; 'DriveLetter'=$_.DriveLetter}}"
            cmd = 'powershell.exe "{}"'.format(ps_cmd)
            out = subprocess.check_output(cmd, shell=True, text=True)
            
            #get drive letter associated with ZIP drive
            for line in out.splitlines():
                if 'ZIP 100' in line:
                      drive_ltr = line.split()[2]
            
            #verify that drive letter is recognized by work station
            try:
                drive_ltr
            except UnboundLocalError:
                print('\n\nNOTE: Zip drive not recognized.  If you have not done so, insert disk into drive and allow device to complete initial loading.')
                return
            
            #match PowerShell output with device name from /proc/partitions
            for line in check_device.splitlines():
                if len(line.split()) == 5 and drive_ltr in line.split()[4]:
                    dd_target = '/dev/{}'.format(line.split()[3])
        
        #if 'other' device (i.e., hard drive or USB drive), verify device name
        elif self.source_device == 'Other':

            if self.other_device in check_device:
                dd_target = '/dev/{}'.format(self.other_device)
            else:
                print('\nNOTE: device name "{}" not found in /proc/partitions; verify and try again.'.format(self.other_device))
                return
        
        else:
            dd_target = self.source_device
            
        print('\n\nDISK IMAGE CREATION: DDRESCUE\n\n\tSOURCE: {} \n\tDESTINATION: {}'.format(dd_target, self.barcode_item.imagefile))
        
        migrate_ver = subprocess.check_output('ddrescue -V', shell=True, text=True).split('\n', 1)[0]  
        
        timestamp1 = str(datetime.datetime.now())
        
        image_cmd1 = 'ddrescue -n {} {} {}'.format(dd_target, self.barcode_item.imagefile, self.barcode_item.mapfile)
    
        #run commands via subprocess; per ddrescue instructions, we need to run it twice    
        print('\n--------------------------------------First pass with ddrescue------------------------------------\n')
        exitcode1 = subprocess.call(image_cmd1, shell=True, text=True)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp1, 'disk image creation', exitcode1, image_cmd1, 'First pass; extracted a disk image from the physical information carrier.', migrate_ver, self.barcode_item)
        
        #new timestamp for second pass (recommended by ddrescue developers)
        timestamp2 = str(datetime.datetime.now())
        
        image_cmd2 = 'ddrescue -d -r2 {} {} {}'.format(dd_target, self.barcode_item.imagefile, self.barcode_item.mapfile)
        
        print('\n\n--------------------------------------Second pass with ddrescue------------------------------------\n')
        
        exitcode2 = subprocess.call(image_cmd2, shell=True, text=True)
        
        #record event in PREMIS metadata if successful
        if os.path.exists(self.barcode_item.imagefile) and os.stat(self.barcode_item.imagefile).st_size > 0:
            print('\n\n\tDisk image created; proceeding to next step...')
            exitcode2 = 0
            self.record_premis(timestamp2, 'disk image creation', exitcode2, image_cmd2, 'Second pass; extracted a disk image from the physical information carrier.', migrate_ver, self.barcode_item))
        else:
            print('\n\nDISK IMAGE CREATION FAILED: Indicate any issues in note to collecting unit.')
    
    def disk_image_info(self):
        
        print('\n\nDISK IMAGE METADATA EXTRACTION: FSSTAT, ILS, MMLS')
    
        #run disktype to get information on file systems on disk
        disktype_command = 'disktype {} > {}' % (self.barcode_item.imagefile, self.barcode_item.disktype_output)
            
        timestamp = str(datetime.datetime.now())
        exitcode = subprocess.call(disktype_command, shell=True, text=True)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'forensic feature analysis', exitcode, disktype_command, 'Determined disk image file system information.', 'disktype v9', self.barcode_item)
        
        #get disktype output; get character encoding just in case there's something funky...
        charenc = get_encoding(self.barcode_item.disktype_output)
        
        with open(self.barcode_item.disktype_output, 'r', encoding=charenc) as f:
            dt_out = f.read()
        
        #print disktype output to screen
        print(dt_out, end="")
        
        #get a list of output
        dt_info = dt_out.split('Partition ')
        
        #now loop through the list to get all file systems ID'd by disktype
        fs_list = []
        for dt in dt_info:
            if 'file system' in dt:
                fs_list.append([d for d in dt.split('\n') if ' file system' in d][0].split(' file system')[0].lstrip().lower())
        
        #save file system list for later...
        pickle_dump(self.barcode_item, 'fs_list', fs_list)
        
        #run fsstat: get range of meta-data values (inode numbers) and content units (blocks or clusters)
        fsstat_ver = 'fsstat: %s' % subprocess.check_output('fsstat -V', shell=True, text=True).strip()
        fsstat_command = 'fsstat {} > {} 2>&1'.format(self.barcode_item.imagefile, self.barcode_item.fsstat_output)
        
        timestamp = str(datetime.datetime.now())
        
        try:
            exitcode = subprocess.call(fsstat_command, shell=True, text=True, timeout=60)   
        #if process times out, kill it and mark as failed
        except subprocess.TimeoutExpired:
            for proc in psutil.process_iter():
                if proc.name() == 'fsstat.exe':
                    psutil.Process(proc.pid).terminate()
            exitcode = 1
            
        #record event in PREMIS metadata    
        self.record_premis(timestamp, 'forensic feature analysis', exitcode, fsstat_command, 'Determined range of meta-data values (inode numbers) and content units (blocks or clusters)', fsstat_ver, self.barcode_item)

        #run ils to document inode information
        ils_ver = 'ils: %s' % subprocess.check_output('ils -V', shell=True, text=True).strip()
        ils_command = 'ils -e {} > {} 2>&1'.format(self.barcode_item.imagefile, self.barcode_item.ils_output)
        
        timestamp = str(datetime.datetime.now())
        try:
            exitcode = subprocess.call(ils_command, shell=True, text=True, timeout=60)
        #if the command times out, kill the process and report as a failure
        except subprocess.TimeoutExpired:
            for proc in psutil.process_iter():
                if proc.name() == 'ils.exe':
                    psutil.Process(proc.pid).terminate()
            exitcode = 1
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'forensic feature analysis', exitcode, ils_command, 'Documented all inodes found on disk image.', ils_ver, self.barcode_item)
        
        #run mmls to document the layout of partitions in a volume system
        mmls_ver = 'mmls: %s' % subprocess.check_output('mmls -V', shell=True, text=True).strip()
        mmls_command = 'mmls {} > {} 2>NUL'.format(self.barcode_item.imagefile, self.barcode_item.mmls_output)
        
        timestamp = str(datetime.datetime.now())
        exitcode = subprocess.call(mmls_command, shell=True, text=True) 
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'forensic feature analysis', exitcode, mmls_command, 'Determined the layout of partitions in a volume system.', mmls_ver, self.barcode_item)
        
        #check mmls output for partition information; first make sure there's actually data in the mmls output file
        partition_info_list = []
        
        if os.stat(self.barcode_item.mmls_output).st_size > 0:
            
            with open(self.barcode_item.mmls_output, 'r', encoding='utf8') as f:
                mmls_info = [m.split('\n') for m in f.read().splitlines()[5:]] 
            
            #loop through mmls output; match file system info with that from disktype output
            for mm in mmls_info:
                temp = {}
                for dt in dt_info:
                    if 'file system' in dt and ', {} sectors from {})'.format(mm[0].split()[4].lstrip('0'), mm[0].split()[2].lstrip('0')) in dt:
                        fsname = [d for d in dt.split('\n') if ' file system' in d][0].split(' file system')[0].lstrip().lower()
                        temp['start'] = mm[0].split()[2]
                        temp['desc'] = fsname
                        temp['slot'] = mm[0].split()[1]
                        #now save this dictionary to our list of partition info
                        if not temp in partition_info_list:
                            partition_info_list.append(temp)
            
            #save partition info for later
            pickle_dump(self.barcode_item, 'partition_info_list', partition_info_list)
            
    def disk_image_replication(self):    

        print('\n\nDISK IMAGE FILE REPLICATION: ')
        
        #set our software versions for unhfs and tsk_recover, just in case...
        cmd = 'unhfs 2>&1'
        unhfs_tool_ver = subprocess.check_output(cmd, shell=True, text=True).splitlines()[0]
        tsk_tool_ver = 'tsk_recover: %s ' % subprocess.check_output('tsk_recover -V', text=True).strip()
        
        #now get information on filesystems and (if present) partitions.  We will need to choose which tool to use based on file system; if UDF or ISO9660 present, use TeraCopy; otherwise use unhfs or tsk_recover
        secure_copy_list = ['udf', 'iso9660']
        unhfs_list = ['osx', 'hfs', 'apple', 'apple_hfs', 'mfs', 'hfs plus']
        tsk_list = ['ntfs', 'fat', 'fat12', 'fat16', 'fat32', 'exfat', 'ext2', 'ext3', 'ext4', 'ufs', 'ufs1', 'ufs2', 'ext', 'yaffs2', 'hfs+']
        
        #recover lists
        fs_list = pickle_load(self.barcode_item, 'ls', 'fs_list')
        partition_info_list = pickle_load(self.barcode_item, 'ls','partition_info_list')
        
        #Proceed if any file systems were found; return if none identified
        if len(fs_list) > 0:
        
            print('\n\tDisktype has identified the following file system: ', ', '.join(fs_list))
            
            #now check for any partitions; if none, go ahead and use teracopy, tsk_recover, or unhfs depending on the file system
            if len(partition_info_list) <= 1:

                print('\n\tNo partition information...')
                
                if any(fs in ' '.join(fs_list) for fs in secure_copy_list):
                    self.secure_copy(self.optical_drive_letter())

                elif any(fs in ' '.join(fs_list) for fs in unhfs_list):
                    self.carve_files('unhfs', unhfs_tool_ver, '', self.barcode_item.files_dir)
                
                elif any(fs in ' '.join(fs_list) for fs in tsk_list): 
                    self.carve_files('tsk_recover', tsk_tool_ver, '', self.barcode_item.files_dir)
                
                else:
                    print('\n\tFile system not recognized by tools')
                    
            #if there are one or more partitions, use tsk_recover or unhfs        
            elif len(partition_info_list) > 1:
            
                for partition in partition_info_list:

                    outfolder = os.path.join(self.barcode_item.files_dir, 'partition_{}'.format(partition['slot']))
                    
                    if partition['desc'] in unhfs_list:
                        self.carve_files('unhfs', unhfs_tool_ver, partition['slot'], outfolder)
                                      
                    elif partition['desc'] in tsk_list:
                        carve_files('tsk_recover', tsk_tool_ver, partition['start'], outfolder)
        else:
            print('\n\tNo files to be replicated.')
    
    def optical_drive_letter(self):
        #NOTE: this assumes only 1 optical disk drive is connected to workstation
        drive_cmd = 'wmic logicaldisk get caption, drivetype | FINDSTR /C:"5"'
        drive_ltr = subprocess.check_output(drive_cmd, shell=True, text=True).split()[0]
        return drive_ltr
    
    def carve_files(self, tool, tool_ver, partition, outfolder): 
        
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        
        if tool == 'unhfs':
            
            if partition == '':
                carve_cmd = 'unhfs -sfm-substitutions -resforks APPLEDOUBLE -o "{}" "{}" 2>nul'.format(outfolder, imagefile)
            else:
                carve_cmd = 'unhfs -sfm-substitutions -partition {} -resforks APPLEDOUBLE -o "{}" "{}" 2>nul'.format(partition, outfolder, imagefile)
        
        else:
            
            if partition == '':
                carve_cmd = 'tsk_recover -a {} {}'.format(imagefile, outfolder)
            
            else:
                carve_cmd = 'tsk_recover -a -o {} {} {}'.format(partition, imagefile, outfolder)
            
        print('\n\tTOOL: {}\n\n\tSOURCE: {} \n\n\tDESTINATION: {}\n'.format(tool, imagefile, outfolder))
        
        timestamp = str(datetime.datetime.now())  
        exitcode = subprocess.call(carve_cmd, shell=True)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'replication', exitcode, carve_cmd, "Created a copy of an object that is, bit-wise, identical to the original.", tool_ver)
        
        #if no files were extracted, remove partition folder.
        if not check_files(outfolder) and outfolder != self.barcode_item.files_dir:
            os.rmdir(outfolder)
        
        #if tsk_recover has been run, go through and fix the file MAC times
        if tool == 'tsk_recover' and exitcode == 0:
            
            #generate DFXML with fiwalk
            if not os.path.exists(self.barcode_item.dfxml_output):
                self.produce_dfxml(self.barcode_item.imagefile)
            
            #use DFXML output to get correct MAC times and update files
            self.fix_dates(outfolder)
        
        elif tool == 'unhfs' and os.path.exists(outfolder):
            file_count = sum([len(files) for r, d, files in os.walk(outfolder)])
            print('\t%s files successfully transferred to %s.' % (file_count, outfolder))
            
        print('\n\tFile replication completed; proceed to content analysis.')
    
    def produce_dfxml(self, target):
    
        timestamp = str(datetime.datetime.now())
        
        file_stats = []
        
        #use fiwalk if we have an image file
        if os.path.isfile(target):
            print('\n\nDIGITAL FORENSICS XML CREATION: FIWALK')
            dfxml_ver_cmd = 'fiwalk-0.6.3 -V'
            dfxml_ver = subprocess.check_output(dfxml_ver_cmd, shell=True, text=True).splitlines()[0]
            
            dfxml_cmd = 'fiwalk-0.6.3 -x {} > {}'.format(target, self.barcode_item.dfxml_output)
            
            exitcode = subprocess.call(dfxml_cmd, shell=True, text=True)
                    
            #parse dfxml to get info for later; because large DFXML files pose a challenge; use iterparse to avoid crashing (Note: for DVD jobs we will also get stats on the files themselves later on) 
            print('\n\tCollecting file statistics...\n')
            counter = 0
            for event, element in etree.iterparse(self.barcode_item.dfxml_output, events = ("end",), tag="fileobject"):
                
                #refresh dict for each fileobject
                file_dict = {}
                
                #default values; will make sure that we don't record info about non-allocated files and that we have a default timestamp value
                good = True
                mt = False
                mtime = 'undated'
                target = ''
                size = ''
                checksum = ''
                
                for child in element:
                    
                    if child.tag == "filename":
                        target = child.text
                    if child.tag == "name_type":
                        if child.text != "r":
                            element.clear()
                            good = False
                            break
                    if child.tag == "alloc":
                        if child.text != "1":
                            good = False
                            element.clear()
                            break
                    if child.tag == "unalloc":
                        if child.text == "1":
                            good = False
                            element.clear()
                            break
                    if child.tag == "filesize":
                        size = child.text
                    if child.tag == "hashdigest":
                        if child.attrib['type'] == 'md5':
                            checksum = child.text
                    if child.tag == "mtime":
                        mtime = datetime.datetime.utcfromtimestamp(int(child.text)).isoformat()
                        mt = True
                    if child.tag == "crtime" and mt == False:
                        mtime = datetime.datetime.utcfromtimestamp(int(child.text)).isoformat()
                
                if good and not '' in file_dict.values():
                    file_dict = { 'name' : target, 'size' : size, 'mtime' : mtime, 'checksum' : checksum}
                    file_stats.append(file_dict)
                    
                    counter+=1            
                    print('\r\tWorking on file #: %s' % counter, end='')

                element.clear()
     
        #use custom operation for other cases    
        elif os.path.isdir(target):
            print('\n\nDIGITAL FORENSICS XML CREATION: bdpl_ingest')
            
            dfxml_ver = 'https://github.com/IUBLibTech/bdpl_ingest'
            dfxml_cmd = 'bdpl_ingest.py'
            
            timestamp = str(datetime.datetime.now().isoformat())
            
            done_list = []

            if os.path.exists(self.barcode_item.temp_dfxml):
                with open(self.barcode_item.temp_dfxml, 'r', encoding='utf-8') as f:
                    done_so_far = f.read().splitlines()
                    for d in done_so_far:
                        line = d.split(' | ')
                        done_list.append(line[0])
                        file_dict = { 'name' : line[0], 'size' : line[1], 'mtime' : line[2], 'ctime' : line[3], 'atime' : line[4], 'checksum' : line[5], 'counter' : line[6] }
                        file_stats.append(file_dict)
            
            if len(file_stats) > 0:
                counter = int(file_stats[-1]['counter'])
            else:
                counter = 0
            
            print('\n')
            
            #get total number of files
            total = sum([len(files) for r, d, files in os.walk(target)])
            
            #now loop through, keeping count
            for root, dirnames, filenames in os.walk(target):
                for file in filenames:
                    
                    #check to make sure that we haven't already added info for this file
                    file_target = os.path.join(root, file)
                    if file_target in done_list:
                        continue
                    
                    counter += 1
                    
                    size = os.path.getsize(file_target)
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_target)).isoformat()
                    ctime = datetime.datetime.fromtimestamp(os.path.getctime(file_target)).isoformat()
                    atime = datetime.datetime.fromtimestamp(os.path.getatime(file_target)).isoformat()[:-7]
                    checksum = md5(file_target)
                    
                    file_dict = { 'name' : file_target, 'size' : size, 'mtime' : mtime, 'ctime' : ctime, 'atime' : atime, 'checksum' : checksum, 'counter' : counter }
                    
                    print('\r\tCalculating checksum for file %d out of %d' % (counter, total), end='')
                    
                    file_stats.append(file_dict)
                    
                    #add this file to our 'done list'
                    done_list.append(file_target)
                    
                    #save this list to file just in case we crash...
                    raw_stats = "%s | %s | %s | %s | %s | %s | %s\n" % (file_target, size, mtime, ctime, atime, checksum, counter)
                    with open(self.barcode_item.temp_dfxml, 'a', encoding='utf8') as f:
                        f.write(raw_stats)
            
            print('\n')
            
            dc_namespace = 'http://purl.org/dc/elements/1.1/'
            dc = "{%s}" % dc_namespace
            NSMAP = {None : 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML',
                    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
                    'dc' : dc_namespace}

            dfxml = etree.Element("dfxml", nsmap=NSMAP, version="1.0")
            
            metadata = etree.SubElement(dfxml, "metadata")
            
            dctype = etree.SubElement(metadata, dc + "type")
            dctype.text = "Hash List"
            
            creator = etree.SubElement(dfxml, 'creator')
            
            program = etree.SubElement(creator, 'program')
            program.text = 'bdpl_ingest'
            
            execution_environment = etree.SubElement(creator, 'execution_environment')
            
            start_time = etree.SubElement(execution_environment, 'start_time')
            start_time.text = timestamp
            
            for f in file_stats:
                fileobject = etree.SubElement(dfxml, 'fileobject')
                
                filename = etree.SubElement(fileobject, 'filename')
                filename.text = f['name']
                
                filesize = etree.SubElement(fileobject, 'filesize')
                filesize.text = str(f['size'])

                modifiedtime = etree.SubElement(fileobject, 'mtime')
                modifiedtime.text = f['mtime']
            
                createdtime = etree.SubElement(fileobject, 'ctime')
                createdtime.text = f['ctime']
                
                accesstime = etree.SubElement(fileobject, 'atime')
                accesstime.text = f['atime']
                    
                hashdigest = etree.SubElement(fileobject, 'hashdigest', type='md5')
                hashdigest.text = f['checksum']

            tree = etree.ElementTree(dfxml)
            
            tree.write(self.barcode_item.dfxml_output, pretty_print=True, xml_declaration=True, encoding="utf-8")      
        
        else:
            print('\n\tERROR: %s does not appear to exist...' % target)
            return
        
        #save stats for reporting...            
        with open (self.barcode_item.checksums, 'wb') as f:
            pickle.dump(file_stats, f)
        
        #save PREMIS
        self.record_premis(timestamp, 'message digest calculation', 0, dfxml_cmd, 'Extracted information about the structure and characteristics of content, including file checksums.', dfxml_ver)
        
        print('\n\n\tDFXML creation completed; moving on to next step...')

    def fix_dates(self, outfolder):
        #adapted from Timothy Walsh's Disk Image Processor: https://github.com/CCA-Public/diskimageprocessor
               
        print('\n\nFILE MAC TIME CORRECTION (USING DFXML)')
        
        timestamp = str(datetime.datetime.now())
         
        try:
            for (event, obj) in Objects.iterparse(self.barcode_item.dfxml_output):
                # only work on FileObjects
                if not isinstance(obj, Objects.FileObject):
                    continue

                # skip directories and links
                if obj.name_type:
                    if obj.name_type not in ["r", "d"]:
                        continue

                # record filename
                dfxml_filename = obj.filename
                dfxml_filedate = int(time.time()) # default to current time

                # record last modified or last created date
                try:
                    mtime = obj.mtime
                    mtime = str(mtime)
                except:
                    pass

                try:
                    crtime = obj.crtime
                    crtime = str(crtime)
                except:
                    pass

                # fallback to created date if last modified doesn't exist
                if mtime and (mtime != 'None'):
                    mtime = time_to_int(mtime[:19])
                    dfxml_filedate = mtime
                elif crtime and (crtime != 'None'):
                    crtime = time_to_int(crtime[:19])
                    dfxml_filedate = crtime
                else:
                    continue

                # rewrite last modified date of corresponding file in objects/files
                exported_filepath = os.path.join(outfolder, dfxml_filename)
                if os.path.isdir(exported_filepath):
                    os.utime(exported_filepath, (dfxml_filedate, dfxml_filedate))
                elif os.path.isfile(exported_filepath):
                    os.utime(exported_filepath, (dfxml_filedate, dfxml_filedate)) 
                else:
                    continue

        except (ValueError, xml.etree.ElementTree.ParseError):
            print('\nUnable to read DFXML!')
            pass
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'metadata modification', 0, 'https://github.com/CCA-Public/diskimageprocessor/blob/master/diskimageprocessor.py#L446-L489', 'Corrected file timestamps to match information extracted from disk image.', 'Adapted from Disk Image Processor Version: 1.0.0 (Tim Walsh)')
    
    def lsdvd_check(self, drive_letter):
        
        #get lsdvd version
        cmd = 'lsdvd -V'
        lsdvd_ver = subprocess.run(cmd, shell=True, text=True, capture_output=True).stderr.split(' - ')[0]
        
        #now run lsdvd to get info about DVD, including # of titles
        timestamp = str(datetime.datetime.now())
        lsdvdcmd = 'lsdvd -Ox -x {} > {} 2> NUL'.format(drive_letter, self.barcode_item.lsdvd_out)
        exitcode = subprocess.call(lsdvdcmd, shell=True, text=True)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'metadata extraction', exitcode, lsdvdcmd, 'Extracted content information from DVD, including titles, chapters, audio streams and video.', lsdvd_ver)
        
        #now verify how many titles are on the disk.  Set a default value of 0
        titlecount = 0
        
        #check file to see how many titles are on DVD using lsdvd XML output. 
        parser = etree.XMLParser(recover=True)

        try:
            doc = etree.parse(self.barcode_item.lsdvd_out, parser=parser)
            titlecount = int(doc.xpath("count(//lsdvd//track)"))
            
            #check for PAL content, just in case...
            formats = doc.xpath("//format")
            if [f for f in formats if f.text == 'PAL']:
                title_format = 'PAL'
            else:
                title_format = 'NTSC'
                
        #if lsdvd fails or information not in report, get the title count by parsing directory...
        except (OSError, lxml.etree.XMLSyntaxError):
            titlelist = glob.glob(os.path.join(drive_letter, '**/VIDEO_TS', '*_*_*.VOB'), recursive=True)
            count = []
            for t in titlelist:
                #parse VOB filenames to get # of titles
                count.append(int(t.rsplit('_', 2)[1]))
            if len(count) > 0:
                titlecount = max(set(count))
        
        #if we haven't identified titles (i.e., we do not have a DVD), delete lsdvd output
        if titlecount == 0:
            os.remove(self.barcode_item.lsdvd_out)
            
        return titlecount, title_format
    
    def normalize_dvd_content(self, titlecount, drive_letter):

        #check current directory; change to a temp directory to store files
        bdpl_cwd = 'C:\\BDPL\\scripts'
        
        if not os.path.exists(self.barcode_item.ffmpeg_temp_dir):
            os.makedirs(self.barcode_item.ffmpeg_temp_dir)
        
        os.chdir(self.barcode_item.ffmpeg_temp_dir)
        
        #get ffmpeg version
        ffmpeg_ver =  '; '.join(subprocess.check_output('"C:\\Program Files\\ffmpeg\\bin\\ffmpeg" -version', shell=True, text=True).splitlines()[0:2])
        
        print('\n\nMOVING IMAGE FILE NORMALIZATION: FFMPEG')
        
        #loop through titles and rip each one to mpeg using native streams
        for title in range(1, (titlecount+1)):
            titlelist = glob.glob(os.path.join(drive_letter, "**/VIDEO_TS", "VTS_%s_*.VOB" % str(title).zfill(2)), recursive=True)
            #be sure list is sorted
            sorted(titlelist)
            
            if len(titlelist) > 0:
                
                #check if title track is missing audio--could make trouble for other tracks...
                audio_test = {}
                print('\n\tChecking audio streams...')
                for t in titlelist:
                    cmd = "ffprobe -i %s -hide_banner -show_streams -select_streams a -loglevel error" % t
                    try:
                        audio_check = subprocess.check_output(cmd, shell=True, text=True)
                        audio_test[t] = audio_check
                    except subprocess.CalledProcessError:
                        pass
                
                if len(audio_test) == 0:
                    print('\nWARNING: unable to access information on DVD. Moving image normalization has failed...')
                    return
                
                #if there's no audio in any track, it's OK
                if all(value == '' for value in audio_test.values()):
                    pass
                    
                #if our first track lacks audio, add a dummy track
                elif audio_test[titlelist[0]] == '':
                    
                    cmd = "ffmpeg -y -nostdin -loglevel warning -i {} -f lavfi -i anullsrc -c:v copy -c:a aac -shortest -target ntsc-dvd {{}".format(titlelist[0], self.barcode_item.dummy_audio)
                    
                    print('\n\tCorrecting missing audio on first track...')
                    
                    subprocess.call(cmd, text=True)
                    
                    #replace original item from list
                    del titlelist[0]
                    titlelist.insert(0, dummy_audio)
                
                timestamp = str(datetime.datetime.now())
                
                ffmpegout = os.path.join(self.barcode_item.files_dir, '{}-{}.mpg'.format(self.barcode_item.item_barcode, str(title).zfill(2)))
                ffmpeg_cmd = 'ffmpeg -y -nostdin -loglevel warning -report -stats -i "concat:{}" -c copy -target ntsc-dvd {}'.format('|'.join(titlelist), ffmpegout)
                
                print('\n\tGenerating title {} of {}: {}\n'.format(str(title), str(titlecount), ffmpegout))
                
                exitcode = subprocess.call(ffmpeg_cmd, shell=True, text=True)
                
                #record event in PREMIS metadata                
                self.record_premis(timestamp, 'normalization', exitcode, ffmpeg_cmd, 'Transformed object to an institutionally supported preservation format (.MPG) with a direct copy of all streams.', ffmpeg_ver)
                
                #move and rename ffmpeg log file
                ffmpeglog = glob.glob(os.path.join(self.barcode_item.ffmpeg_temp_dir, 'ffmpeg-*.log'))[0]
                shutil.move(ffmpeglog, os.path.join(self.barcode_item.log_dir, '{}-{}-ffmpeg.log'.format(item_barcode, str(title).zfill(2))))
                
        #move back to original directory
        os.chdir(bdpl_cwd)
        
        print('\n\tMoving image normalization completed; proceed to content analysis.')

    def cdda_image_creation(self):
        
        print('\n\nDISK IMAGE CREATION: CDRDAO\n\n\tSOURCE: %s \n\tDESTINATION: %s' % (sourceDevice, image_dir))
        
        #determine appropriate drive ID for cdrdao; save output of command to temp file
        scan_cmd = 'cdrdao scanbus > {} 2>&1'.format(self.barcode_item.cdr_scan)
        
        subprocess.check_output(scan_cmd, shell=True, text=True)

        #pull drive ID and cdrdao version from file
        with open(self.barcode_item.cdr_scan, 'r') as f:
            info = f.read().splitlines()
        cdrdao_ver = info[0].split(' - ')[0]
        drive_id = info[8].split(':')[0]
            
        #get info about CD using cdrdao; record this as a premis event, too.
        cdrdao_cmd = 'cdrdao disk-info --device {} --driver generic-mmc-raw > {} 2>&1' % (drive_id, self.barcode_item.disk_info_report)
        timestamp = str(datetime.datetime.now())
        exitcode = subprocess.call(cdrdao_cmd, shell=True, text=True)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'metadata extraction', exitcode, cdrdao_cmd, 'Extracted information about the CD-R, including medium, TOC type, number of sessions, etc.', cdrdao_ver)

        #read log file to determine # of sessions on disk.
        with open(self.barcode_item.disk_info_report, 'r') as f:
            for line in f:
                if 'Sessions             :' in line:
                    sessions = int(line.split(':')[1].strip())
        
        t2c_ver = subprocess.check_output('toc2cue -V', shell=True, text=True).strip()
        
        #for each session, create a bin/toc file
        for x in range(1, (sessions+1)):
            cdr_bin = os.path.join(self.barcode_item.image_dir, "{}-{}.bin").format(self.barcode_item.item_barcode, str(x).zfill(2))
            cdr_toc = os.path.join(self.barcode_item.image_dir, "{}-{}.toc").format(self.barcode_item.item_barcode, str(x).zfill(2))
            cdr_log = os.path.join(self.barcode_item.image_dir, "{}-{}.log").format(self.barcode_item.item_barcode, str(x).zfill(2))
            
            print('\n\tGenerating session {} of {}: {}\n\n'.format(str(x), str(sessions), cdr_bin))
            
            #create separate bin/cue for each session
            cdr_cmd = 'cdrdao read-cd --read-raw --session %s --datafile %s --device %s --driver generic-mmc-raw -v 3 %s | tee -a %s' % (str(x), cdr_bin, drive_id, cdr_toc, cdr_log)
            
            timestamp = str(datetime.datetime.now())
            
            #record event in PREMIS metadata
            exitcode = subprocess.call(cdr_cmd, shell=True, text=True)
            
            self.record_premis(timestamp, 'disk image creation', exitcode, cdr_cmd, 'Extracted a disk image from the physical information carrier.', cdrdao_ver)
                        
            #convert TOC to CUE
            cue = os.path.join(self.barcode_item.image_dir, "{}-{}.cue").format(self.barcode_item.item_barcode, str(sessions).zfill(2))
            cue_log = os.path.join(self.barcode_item.log_dir, "{}-{}_toc2cue.log").format(self.barcode_item.item_barcode, str(sessions).zfill(2))
            t2c_cmd = 'toc2cue {} {} > {} 2>&1'.format(cdr_toc, cue, cue_log)
            timestamp = str(datetime.datetime.now())
            exitcode2 = subprocess.call(t2c_cmd, shell=True, text=True)
            
            #toc2cue may try to encode path information as binary data--let's fix that
            with open(cue, 'rb') as infile:
                cue_info = infile.readlines()[1:]
            
            with open(cue, 'w') as outfile:
                outfile.write('FILE "%s" BINARY\n' % os.path.basename(cdr_bin))
            
            with open(cue, 'ab') as outfile:
                for line in cue_info:
                    outfile.write(line)           
            
            #record event in PREMIS metadata
            self.record_premis(timestamp, 'metadata modification', exitcode2, t2c_cmd, "Converted the CD's table of contents (TOC) file to the CUE format.", t2c_ver)
            
            #place a copy of the .cue file for the first session in files_dir for the forthcoming WAV; this session will have audio data
            if x == 1:
                new_cue = os.path.join(self.barcode_item.files_dir, '{}.cue'.format(self.barcode_item.item_barcode))
                
                #now write the new cue file
                with open(new_cue, 'w') as outfile:
                    outfile.write('FILE "{}.wav" WAVE\n'format(self.barcode_item.item_barcode))
                    
                with open(new_cue, 'ab') as outfile:
                    for line in cue_info:
                        outfile.write(line)
        
        print('\n\tCDDA disk image created; moving on to next step...')

    def cdda_wav_creation(self):

        #get cdparanoia version
        ver_cmd = 'cd-paranoia -V'    
        paranoia_ver = subprocess.run(ver_cmd, shell=True, text=True, capture_output=True).stderr.splitlines()[0]
        
        print('\n\nAUDIO CONTENT NORMALIZATION: CDPARANOIA\n\n\tSOURCE: {} \n\tDESTINATION: {}\n'.format(self.source_device, self.barcode_item.paranoia_out))
        
        paranoia_cmd = 'cd-paranoia -l {} -w [00:00:00.00]- {}'format(self.barcode_item.paranoia_log, self.barcode_item.paranoia_out)
        
        timestamp = str(datetime.datetime.now())
        exitcode = subprocess.call(paranoia_cmd, shell=True, text=True)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'normalization', exitcode, paranoia_cmd, 'Transformed object to an institutionally supported preservation format (.WAV).', paranoia_ver)
        
        print('\n\tAudio normalization complete; proceed to content analysis.')
    
    def run_antivirus(self):
       
        #get version
        cmd = 'clamscan -V'
        av_ver = subprocess.check_output(cmd, text=True).rstrip()

        av_command = 'clamscan -i -l {} --recursive {}'.format(self.barcode_item.virus_log, self.barcode_item.files_dir)  
        
        timestamp = str(datetime.datetime.now())
        exitcode = subprocess.call(av_command, shell=True, text=True)
        
        #store virus scan results in metadata_dict
        with open(virus_log, 'r') as f:
            if "Infected files: 0" not in f.read():
                self.barcode_item.metadata_dict['virus_scan_results'] = 'WARNING! Virus or malware found; see %s.' % virus_log
            
            else:
                self.barcode_item.metadata_dict['virus_scan_results'] = '-'

        #save metadata_dict to file, just in case
        pickle_dump(self.barcode_item, 'metadata_dict', self.barcode_item.metadata_dict)
        
        #save preservation to PREMIS
        self.record_premis(timestamp, 'virus check', exitcode, av_command, 'Scanned files for malicious programs.', av_ver)
        
        print('\n\tVirus scan completed; moving on to next step...')

    def run_bulkext(self):

        #get bulk extractor version for premis
        try:
            be_ver = subprocess.check_output(['bulk_extractor', '-V'], shell=True, text=True).rstrip()
        except subprocess.CalledProcessError as e:
            be_ver = e.output.rstrip()
        
        print('\n\tScan underway...be patient!\n')
        
        #use default command with buklk_extractor
        bulkext_command = 'bulk_extractor -x aes -x base64 -x elf -x exif -x gps -x hiberfile -x httplogs -x json -x kml -x net -x pdf -x sqlite -x winlnk -x winpe -x winprefetch -S ssn_mode=2 -q -1 -o "{}" -R "{}" > "{}"'.format(self.barcode_item.bulkext_dir, self.barcode_item.files_dir, self.barcode_item.bulkext_log)
        
        if os.path.exists(self.barcode_item.bulkext_dir):
            shutil.rmtree(self.barcode_item.bulkext_dir)
        
        try:
            os.makedirs(self.barcode_item.bulkext_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        #create timestamp
        timestamp = str(datetime.datetime.now())        

        exitcode = subprocess.call(bulkext_command, shell=True, text=True)
       
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'sensitive data scan', exitcode, bulkext_command, 'Scanned files for potentially sensitive information, including Social Security and credit card numbers.', be_ver)
        
        #create a cumulative BE report
        if os.path.exists(self.barcode_item.cumulative_be_report):
            os.remove(self.barcode_item.cumulative_be_report)
            
        for myfile in ('pii.txt', 'ccn.txt', 'email.txt', 'telephone.txt', 'find.txt'):
            myfile = os.path.join(self.barcode_item.bulkext_dir, myfile)
            if os.path.exists(myfile) and os.stat(myfile).st_size > 0:
                with open(myfile, 'rb') as filein:
                    data = filein.read().splitlines()    
                with open(self.barcode_item.cumulative_be_report, 'a', encoding='utf8') as outfile:
                    outfile.write('%s: %s\n' % (os.path.basename(myfile), len(data[5:])))
        
        #if no results from the above, create file so we don't throw an error later
        if not os.path.exists(self.barcode_item.cumulative_be_report):         
            open(self.barcode_item.cumulative_be_report, 'a').close()

        #move any b_e histogram files, if needed
        for myfile in ('email_domain_histogram.txt', 'find_histogram.txt', 'telephone_histogram.txt'):
            current_file = os.path.join(self.barcode_item.bulkext_dir, myfile)
            try:    
                if os.stat(current_file).st_size > 0:
                    shutil.copy(current_file, self.barcode_item.reports_dir)
            except OSError:
                continue
        
        print('\n\tSensitive data scan completed; moving on to next step...')
    
    def format_analysis(self):
    
        print('\n\tFile format identification with Siegfried...') 

        format_version = subprocess.check_output('sf -version', shell=True, text=True).replace('\n', ' ')
        
        #remove Siegrfried report if it already exists
        if os.path.exists(self.barcode_item.sf_file):
            os.remove(self.barcode_item.sf_file)                                                                 
                
        format_command = 'sf -z -csv "{}" > "{}"'.format(self.barcode_item.files_dir, self.barcode_item.sf_file)
        
        #create timestamp
        timestamp = str(datetime.datetime.now())
        
        exitcode = subprocess.call(format_command, shell=True, text=True)
        
        #if siegfried fails, then we'll run DROID
        if exitcode != 0 and os.path.getsize(sf_file) == 0:
            print('\n\tFile format identification with siegfried failed; now attempting with DROID...\n') 
            
            format_version = "DROID v%s" % subprocess.check_output('droid -v', shell=True, text=True).strip()
            
            droid_cmd1 = 'droid -RAq -a "{}" -p "{}"' % (self.barcode_item.files_dir, self.barcode_item.droid_profile)
            
            exitcode = subprocess.call(droid_cmd1, shell=True)
            
            droid_cmd2 = 'droid -p "{}" -e "{}"'.format(self.barcode_item.droid_profile, self.barcode_item.droid_out)
            
            subprocess.call(droid_cmd2, shell=True)
            
            #consolidate commands for premis
            format_command = "{} && {}".format(droid_cmd1, droid_cmd2)
            
            #now reformat droid output to be like sf output
            droid_to_siegfried(self.barcode_item.droid_out, self.barcode_item.sf_file)
        
        #record event in PREMIS metadata
        self.record_premis(timestamp, 'format identification', exitcode, format_command, 'Determined file format and version numbers for content using the PRONOM format registry.', format_version)

    def import_csv(self):

        conn = sqlite3.connect(self.barcode_item.siegfried_db)
        conn.text_factory = str  # allows utf-8 data to be stored
        cursor = conn.cursor()

        print('\n\tImporting siegried file to sqlite3 database...')
        """Import csv file into sqlite db"""
        f = open(self.barcode_item.sf_file, 'r', encoding='utf8')
        
        try:
            reader = csv.reader(x.replace('\0', '') for x in f) # replace null bytes with empty strings on read
        except UnicodeDecodeError:
            f = (x.strip() for x in f) # skip non-utf8 encodable characters
            reader = csv.reader(x.replace('\0', '') for x in f) # replace null bytes with empty strings on read
        header = True
        for row in reader:
            if header:
                header = False # gather column names from first row of csv
                sql = "DROP TABLE IF EXISTS siegfried"
                cursor.execute(sql)
                sql = "CREATE TABLE siegfried (filename text, filesize text, modified text, errors text, namespace text, id text, format text, version text, mime text, basis text, warning text)"
                cursor.execute(sql)
                insertsql = "INSERT INTO siegfried VALUES (%s)" % (", ".join([ "?" for column in row ]))
                rowlen = len(row)
            else:
                # skip lines that don't have right number of columns
                if len(row) == rowlen:
                    cursor.execute(insertsql, row)
        conn.commit()
        f.close()
        
        #create file to indicate that this operation has completed
        open(self.barcode_item.sqlite_done, 'a').close()
        
        cursor.close()
        conn.close()

    def stats_and_report_creation(self):
            
        #set up html for report
        html_doc = open(self.barcode_item.temp_html, 'w', encoding='utf8')
        
        #prepare sqlite database and variables
        conn = sqlite3.connect(self.barcode_item.siegfried_db)
        conn.text_factory = str  # allows utf-8 data to be stored
        cursor = conn.cursor() 
        
        """Get aggregate statistics and write to html report"""
        self.get_stats(cursor, html_doc) # get aggregate stats and write to html file
        generate_reports(cursor, html_doc, folders, re_analyze, item_barcode) # run sql queries, print to html and csv
        close_html(html_doc) # close HTML file tags
        
        # close database connections
        cursor.close()
        conn.close()
        
        print('\n\tFormat analysis completed!')
        
        # close HTML file
        html_doc.close()

        # write new html file, with hrefs for PRONOM IDs           
        if os.path.exists(self.barcode_item.new_html):
            os.remove(self.barcode_item.new_html)

        write_pronom_links(self.barcode_item.temp_html, self.barcode_item.new_html)
        
        fileformats = []
        formatcount = 0
        formatlist = ''
        formatcsv = os.path.join(self.barcode_item.reports_dir, 'formats.csv')
        try:
            with open(formatcsv, 'r') as csvfile:
                formatreader = csv.reader(csvfile)
                next(formatreader)
                for row in formatreader:
                    formatcount += 1
                    fileformats.append(row[0])
                fileformats = [element or 'Unidentified' for element in fileformats] # replace empty elements with 'Unidentified'
                if formatcount > 0:
                    self.barcode_item.metadata_dict['format_overview'] = "Top file formats (out of %s total) are: %s" % (formatcount, ' | '.join(fileformats[:10]))
                else:
                    self.barcode_item.metadata_dict['format_overview'] = "-"
                
        except IOError:
            self.barcode_item.metadata_dict['format_overview'] = "ERROR! No formats.csv file to pull formats from."
        
        #save metadata_dict, just in case...
        pickle_dump(self.barcode_item, 'metadata_dict', self.barcode_item.metadata_dict)
    
    def get_stats(self, cursor, html_doc):
        print('\n\tGetting statistics about content...')
        
        # get stats from sqlite db
        cursor.execute("SELECT COUNT(*) from siegfried;") # total files
        num_files = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) from siegfried where filesize='0';") # empty files
        empty_files = cursor.fetchone()[0]
        
        #for DVDs, we will use stats from normalized files; however, we will also need disk image stats
        if self.job_type == 'DVD':
            file_stats = []
            for f in os.listdir(self.barcode_item.files_dir):
                file = os.path.join(self.barcode_item.files_dir, f)
                file_dict = {}
                size = os.path.getsize(file)
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file)).isoformat()
                ctime = datetime.datetime.fromtimestamp(os.path.getctime(file)).isoformat()
                atime = datetime.datetime.fromtimestamp(os.path.getatime(file)).isoformat()[:-7]
                checksum = self.md5(file)
                
                file_dict = { 'name' : file, 'size' : size, 'mtime' : mtime, 'ctime' : ctime, 'atime' : atime, 'checksum' : checksum}
                file_stats.append(file_dict)
            
            try:
                with open(self.barcode_item.checksums, 'rb') as f:
                    file_stats_di = pickle.load(f)
            except FileNotFoundError:
                pass
        else:
            file_stats = []
            try:
                with open(self.barcode_item.checksums, 'rb') as f:
                    file_stats = pickle.load(f)
            except FileNotFoundError:
                pass
            
        #Get stats on duplicates. Just in case the bdpl ingest tool crashes after compiling a duplicates list, we'll check to see if it already exists
        dup_list = []
        if os.path.exists(self.barcode_item.duplicates) and not self.re_analyze:
            dup_list = pickle_load(self.barcode_item, 'ls', 'duplicates')
        else:
            #next, create a new dictionary that IDs checksums that correspond to 1 or more files. NOTE: the 'file_stats' list will be empty for DVDs, so we'll skip this step in that case
            if len(file_stats) > 1:
                stat_dict = {}
                for dctnry in file_stats:
                    if int(dctnry['size']) > 0:
                        if dctnry['checksum'] in stat_dict:
                            stat_dict[dctnry['checksum']].append(dctnry['name'])
                        else:
                            stat_dict[dctnry['checksum']] = [dctnry['name']]
               
                #go through new dict and find checksums with duplicates
                for chksm in [key for key, values in stat_dict.items() if len(values) > 1]:
                    for fname in stat_dict[chksm]:
                        temp = [item for item in file_stats if item['checksum'] == chksm and item['name'] == fname][0]
                        dup_list.append([temp['name'], temp['size'], temp['mtime'], temp['checksum']])
                
            #save this duplicate file for later when we need to write to html
            pickle_dump(self.barcode_item, 'duplicates', dup_list)
        
        #total duplicates = total length of duplicate list
        all_dupes = len(dup_list)

        #distinct duplicates = # of unique checksums in the duplicates list
        distinct_dupes = len(set([c[3] for c in dup_list]))

        #duplicate copies = # of unique files that may have one or more copies
        duplicate_copies = int(all_dupes) - int(distinct_dupes) # number of duplicate copies of unique files
        duplicate_copies = str(duplicate_copies)
        
        distinct_files = int(num_files) - int(duplicate_copies)
        distinct_files = str(distinct_files)
            
        cursor.execute("SELECT COUNT(*) FROM siegfried WHERE id='UNKNOWN';") # unidentified files
        unidentified_files = cursor.fetchone()[0]

        #next get date information using info pulled from dfxml
        date_info = []
        
        #for dvd jobs, we need to use disk image metadata for dates...
        if self.job_type == 'DVD':
            file_stats = file_stats_di
        
        #let's not accept file mtimes that were set when content was replicated.  Compare file time against timestamp for replication...
        premis_list = pickle_load(self.barcode_item, 'ls', 'premis_list')
        
        try:
            bdpl_time = [p for p in premis_list if p['eventType'] == 'replication'][0]['timestamp'].split('.')[0].replace('T', ' ')
        except IndexError:
            bdpl_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.barcode_item.folders_created)).isoformat().replace('T', ' ').split('.')[0]
        
        bdpl_time = datetime.datetime.strptime(bdpl_time, "%Y-%m-%d %H:%M:%S")
        
        if len(file_stats) > 0:
            for dctnry in file_stats:
                dt_time = dctnry['mtime'].replace('T', ' ').split('.')[0]
                dt_time = datetime.datetime.strptime(dt_time, "%Y-%m-%d %H:%M:%S")
                if dt_time < bdpl_time:
                    date_info.append(dctnry['mtime'])
                else:
                    date_info.append('undated')
            
            #remove all occurences of 'undated', to get better info
            date_info_check = [x for x in date_info if x != 'undated']
            
            if len(date_info_check) > 0:
                begin_date = min(date_info_check)[:4]
                end_date = max(date_info_check)[:4]
                earliest_date = min(date_info_check)
                latest_date = max(date_info_check)   
            
            else:
                begin_date = "undated"
                end_date = "undated"
                earliest_date = "undated"
                latest_date = "undated"
        
        else:
            begin_date = "undated"
            end_date = "undated"
            earliest_date = "undated"
            latest_date = "undated"
            
        #generate a year count
        year_info = [x[:4] for x in date_info]
        year_info = [x if x != 'unda' else 'undated' for x in year_info]
        
        year_count = dict(Counter(year_info))
        
        path = os.path.join(self.barcode_item.reports_dir, 'years.csv')    
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            year_header = ['Year Last Modified', 'Count']
            writer.writerow(year_header)
            if len(year_count) > 0:
                for key, value in year_count.items():
                    writer.writerow([key, value])

        cursor.execute("SELECT COUNT(DISTINCT format) as formats from siegfried WHERE format <> '';") # number of identfied file formats
        num_formats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM siegfried WHERE errors <> '';") # number of siegfried errors
        num_errors = cursor.fetchone()[0]

        # calculate size from recursive dirwalk and format
        size_bytes = 0
        for root, dirs, files in os.walk(self.barcode_item.files_dir):
            for f in files:
                file_path = os.path.join(root, f)
                file_info = os.stat(file_path)
                size_bytes += file_info.st_size

        size = self.convert_size(size_bytes)
        
        # write html
        html_doc.write('<!DOCTYPE html>')
        html_doc.write('\n<html lang="en">')
        html_doc.write('\n<head>')
        html_doc.write('\n<title>IUL Born Digital Preservation Lab report: %s</title>' % self.barcode_item.item_barcode)
        html_doc.write('\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
        html_doc.write('\n<meta name="description" content="HTML report based upon a template developed by Tim Walsh and distributed as part of Brunnhilde v. 1.7.2">')
        html_doc.write('\n<link rel="stylesheet" href="./assets//css/bootstrap.min.css">')
        html_doc.write('\n</head>')
        html_doc.write('\n<body style="padding-top: 80px">')
        # navbar
        html_doc.write('\n<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">')
        html_doc.write('\n<a class="navbar-brand" href="#">Brunnhilde</a>')
        html_doc.write('\n<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">')
        html_doc.write('\n<span class="navbar-toggler-icon"></span>')
        html_doc.write('\n</button>')
        html_doc.write('\n<div class="collapse navbar-collapse" id="navbarNavAltMarkup">')
        html_doc.write('\n<div class="navbar-nav">')
        html_doc.write('\n<a class="nav-item nav-link" href="#Provenance">Provenance</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Stats">Statistics</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#File formats">File formats</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#File format versions">Versions</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#MIME types">MIME types</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Last modified dates by year">Dates</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Unidentified">Unidentified</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Errors">Errors</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Duplicates">Duplicates</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Personally Identifiable Information (PII)">PII</a>')
        html_doc.write('\n<a class="nav-item nav-link" href="#Named Entities">Named Entities</a>')
        html_doc.write('\n</div>')
        html_doc.write('\n</div>')
        html_doc.write('\n</nav>')
        # content
        html_doc.write('\n<div class="container-fluid">')
        html_doc.write('\n<h1 style="text-align: center; margin-bottom: 40px;">IUL BDPL Brunnhilde HTML report</h1>')
        # provenance
        html_doc.write('\n<a name="Provenance" style="padding-top: 40px;"></a>')
        html_doc.write('\n<div class="container-fluid" style="margin-bottom: 40px;">')
        html_doc.write('\n<div class="card">')
        html_doc.write('\n<h2 class="card-header">Provenance</h2>')
        html_doc.write('\n<div class="card-body">')
        '''need to check if disk image or not'''
        if jobType == 'Copy_only':
            html_doc.write('\n<p><strong>Input source: File directory</strong></p>')
        elif jobType == 'DVD':
            html_doc.write('\n<p><strong>Input source: DVD-Video (optical disc)</strong></p>')
        elif jobType == 'CDDA':
            html_doc.write('\n<p><strong>Input source: Compact Disc Digital Audio</strong></p>')
        elif jobType == 'Disk_image':
            html_doc.write('\n<p><strong>Input source: Physical media</strong></p>')
            
        html_doc.write('\n<p><strong>Item identifier:</strong> %s</p>' % self.barcode_item.item_barcode)
        html_doc.write('\n</div>')
        html_doc.write('\n</div>')
        html_doc.write('\n</div>')
        # statistics
        html_doc.write('\n<a name="Stats" style="padding-top: 40px;"></a>')
        html_doc.write('\n<div class="container-fluid" style="margin-bottom: 40px;">')
        html_doc.write('\n<div class="card">')
        html_doc.write('\n<h2 class="card-header">Statistics</h2>')
        html_doc.write('\n<div class="card-body">')
        html_doc.write('\n<h4>Overview</h4>')
        html_doc.write('\n<p><strong>Total files:</strong> %s (includes contents of archive files)</p>' % num_files)
        html_doc.write('\n<p><strong>Total size:</strong> %s</p>' % size)
        html_doc.write('\n<p><strong>Years (last modified):</strong> %s - %s</p>' % (begin_date, end_date))
        html_doc.write('\n<p><strong>Earliest date:</strong> %s</p>' % earliest_date)
        html_doc.write('\n<p><strong>Latest date:</strong> %s</p>' % latest_date)
        html_doc.write('\n<h4>File counts and contents</h4>')
        html_doc.write('\n<p><em>Calculated by hash value. Empty files are not counted in first three categories. Total files = distinct + duplicate + empty files.</em></p>')
        html_doc.write('\n<p><strong>Distinct files:</strong> %s</p>' % distinct_files)
        html_doc.write('\n<p><strong>Distinct files with duplicates:</strong> %s</p>' % distinct_dupes)
        html_doc.write('\n<p><strong>Duplicate files:</strong> %s</p>' % duplicate_copies)
        html_doc.write('\n<p><strong>Empty files:</strong> %s</p>' % empty_files)
        html_doc.write('\n<h4>Format identification</h4>')
        html_doc.write('\n<p><strong>Identified file formats:</strong> %s</p>' % num_formats)
        html_doc.write('\n<p><strong>Unidentified files:</strong> %s</p>' % unidentified_files)
        html_doc.write('\n<h4>Errors</h4>')
        html_doc.write('\n<p><strong>Siegfried errors:</strong> %s</p>' % num_errors)
        html_doc.write('\n<h2>Virus scan report</h2>')
        with open(self.barcode_item.virus_log, 'r', encoding='utf-8') as f:
            virus_report = f.read()
        html_doc.write('\n<p>%s</p>' % virus_report)
        html_doc.write('\n</div>')
        html_doc.write('\n</div>')
        html_doc.write('\n</div>')
        # detailed reports
        html_doc.write('\n<div class="container-fluid" style="margin-bottom: 40px;">')
        html_doc.write('\n<div class="card">')
        html_doc.write('\n<h2 class="card-header">Detailed reports</h2>')
        html_doc.write('\n<div class="card-body">')
        
        #save information to metadata_dict     
        self.barcode_item.metadata_dict.update({'Source': item_barcode, 'begin_date': begin_date, 'end_date' : end_date, 'extent_normal': size, 'extent_raw': size_bytes, 'item_file_count': num_files, 'item_duplicate_count': distinct_dupes, 'FormatCount': num_formats, 'item_unidentified_count': unidentified_files})  
        
        #save metadata_dict to file just in case...
        pickle_dump(self.barcode_item, 'metadata_dict', self.barcode_item.metadata_dict)
    
    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def convert_size(self, size):
        # convert size to human-readable form
        if (size == 0):
            return '0 bytes'
        size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p)
        s = str(s)
        s = s.replace('.0', '')
        return '%s %s' % (s,size_name[i])
    
    def record_premis(self, timestamp, event_type, event_outcome, event_detail, event_detail_note, agent_id):
        
        #retrieve our premis_list
        premis_list = pickle_load(self.barcode_item, 'ls', 'premis_list')
        
        temp_premis = []
        
        temp_dict = {}
        temp_dict['eventType'] = event_type
        temp_dict['eventOutcomeDetail'] = event_outcome
        temp_dict['timestamp'] = timestamp
        temp_dict['eventDetailInfo'] = event_detail
        temp_dict['eventDetailInfo_additional'] = event_detail_note
        temp_dict['linkingAgentIDvalue'] = agent_id
        
        temp_premis.append(temp_dict)
        
        #JUST IN CASE: check to see if we've already written to a premis file (may happen if we have to rerun procedures)
        if os.path.exists(self.barcode_item.premis_path):
            
            #check to see if operation has already been completed (we'll write an empty file once we've done so)
            premis_xml_included = os.path.join(self.barcode_item.temp_dir, 'premis_xml_included.txt')
            if not os.path.exists(premis_xml_included):
            
                temp_premis = []
            
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
                    
                    if not temp_dict in temp_premis:
                        temp_premis.append(temp_dict)
                    
                #now sort based on ['timestamp'] to make sure we're in chronological order
                temp_premis.sort(key=lambda x:x['timestamp'])
                
                #now create our premis_xml_included.txt file so we don't go through this again.
                open(premis_xml_included, 'a').close()

        #now save our premis list
        pickle_dump(self.barcode_item, 'premis_list', premis_list)

    def check_files(self, some_dir):
        #check to see if it exists
        if not os.path.exists(some_dir):
            print('\n\nError; folder "%s" does not exist.' % some_dir)
            return False
        
        #make sure there are files in the 'files' directory
        for dirpath, dirnames, contents in os.walk(some_dir):
            for file in contents:
                if os.path.isfile(os.path.join(dirpath, file)):
                    #return True as soon as a file is found
                    return True
                else: 
                    continue
        
        #if no files found, return false
        return False

    def check_premis(self, term):
        #check to see if an event is already in our premis list--i.e., it's been successfully completed.  Currently only used for most resource-intensive operations: virus scheck, sensitive data scan, format id, and checksum calculation.
        
        #set up premis_list
        premis_list = pickle_load(self.barcode_item, 'ls', 'premis_list')
        
        #see if term has been recorded at all
        found = [dic for dic in premis_list if dic['eventType'] == term]
        
        #if not recorded, it hasn't been run
        if not found: 
            return False
        else:
            #for virus scans, we will assume that completion may have either a 0 or non-zero value.  No need to run again.
            if term == 'virus check':
                return True
            elif term == 'metadata extraction':
                if [dc for dc in found if 'tree v1.7.0' in dc['linkingAgentIDvalue']]:
                    return True
            #for other microservices, check if operation completed successfully; if so, return True, otherwise False
            else:
                if [dc for dc in found if dc['eventOutcomeDetail'] in ['0', 0]]:
                    return True
                else:
                    return False

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

def pickle_load(current_barcode_item, array_type, array_name):
        
    temp_file = os.path.join(current_barcode_item.temp_dir, '{}.txt'.format(array_name))
    
    if array_type == 'ls':
        temp_array = []
    elif array_type == 'dict':
        temp_array = {}
    
    #make sure there's something in the file
    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
        with open(temp_file, 'rb') as file:
            temp_array = pickle.load(file)
                    
    return temp_array

def pickle_dump(current_barcode_item, array_name, array_instance):
    
    temp_file = os.path.join(current_barcode_item.temp_dir, '{}.txt'.format(array_name))
     
    if not os.path.exists(current_barcode_item.temp_dir):
        os.makedirs(current_barcode_item.temp_dir)
        
    with open(temp_file, 'wb') as file:
        pickle.dump(array_instance, file)

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
