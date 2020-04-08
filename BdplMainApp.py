#!/usr/bin/env python3

import chardet
from collections import OrderedDict
from collections import Counter
import csv
import datetime
import errno
import fnmatch
import glob
import hashlib
from lxml import etree
import math
import openpyxl
import os
import pickle
import psutil
import re
import shelve
import shutil
import sqlite3
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from urllib.parse import unquote
import urllib.request
import uuid
import webbrowser
import zipfile

# from dfxml project
import Objects

#BDPL files
from BdplObjects import Unit, Shipment, ItemBarcode, Spreadsheet, ManualPremisEvent, RipstationBatch

#set up as controller
class BdplMainApp(tk.Tk):
    def __init__(self, bdpl_work_dir, bdpl_archiver_dir):
        tk.Tk.__init__(self)
        self.geometry("+0+0")
        self.title("Indiana University Library Born-Digital Preservation Lab")
        self.iconbitmap(r'C:/BDPL/scripts/favicon.ico')
        self.protocol('WM_DELETE_WINDOW', lambda: close_app(self))

        self.bdpl_work_dir = bdpl_work_dir
        self.bdpl_archiver_dir = bdpl_archiver_dir
        self.bdpl_resources = os.path.join(bdpl_work_dir, 'bdpl_resources')
        self.addresses = 'C:/BDPL/resources/addresses.txt'
        self.bdpl_master_spreadsheet = os.path.join(self.bdpl_archiver_dir, 'spreadsheets', 'bdpl_master_spreadsheet.xlsx')
        
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
        self.separations_status = tk.BooleanVar()

        #GUI metadata variables
        self.collection_title = tk.StringVar()
        self.collection_creator = tk.StringVar()
        self.content_source_type = tk.StringVar()
        self.item_title = tk.StringVar()
        self.label_transcription = tk.StringVar()
        self.item_description = tk.StringVar()
        self.appraisal_notes = tk.StringVar()
        self.bdpl_instructions = tk.StringVar()
        
        #GUI vars for RipstationIngest
        self.ripstation_ingest_option = tk.StringVar()
        self.ripstation_log = tk.StringVar()
        self.ripstation_userdata = tk.StringVar()

        #create notebook to start creating app
        self.bdpl_notebook = ttk.Notebook(self)
        self.bdpl_notebook.pack(pady=10, fill=tk.BOTH, expand=True)

        #update info on current tab when it's switched
        self.bdpl_notebook.bind('<<NotebookTabChanged>>', self.update_tab)

        self.tabs = {}

        #other tabs: bag_prep, bdpl_to_mco, RipstationIngest
        app_tabs = {BdplIngest : 'BDPL Ingest',  RipstationIngest : 'RipStation Ingest', SdaDeposit : 'Deposit to SDA'}

        for tab, description in app_tabs.items():
            tab_name = tab.__name__
            new_tab = tab(parent=self.bdpl_notebook, controller=self)
            self.bdpl_notebook.add(new_tab, text = description)

            self.tabs[tab_name] = new_tab

        self.option_add('*tearOff', False)
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
       
        self.actions_ = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.actions_, label='Other actions')
        self.actions_.add_command(label='Check shipment status', command=self.shipment_status)
        self.actions_.add_separator()
        self.actions_.add_command(label='Move media images', command=self.media_images)
        self.actions_.add_separator()
        self.actions_.add_command(label='Add Manual PREMIS event', command= lambda: ManualPremisEvent(self))
        self.actions_.add_separator()
        
        self.connect=tk.Menu(self.actions_)
        self.actions_.add_cascade(menu=self.connect, label = 'Connect to server...')
        self.connect.add_command(label = 'BDPL Workspace', command=lambda:self.connect_to_server('bdpl_workspace'))
        self.connect.add_command(label = 'BDPL Archiver', command=lambda:self.connect_to_server('bdpl_archiver'))
        
        self.help_ = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.help_, label='Help')
        self.help_.add_command(label='Open BDPL wiki', command = lambda: webbrowser.open_new(r"https://wiki.dlib.indiana.edu/display/DIGIPRES/Born+Digital+Preservation+Lab"))

    def get_current_tab(self):
        return self.bdpl_notebook.tab(self.bdpl_notebook.select(), 'text')
        
    def update_tab(self, event):
        event.widget.update_idletasks()

        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight())
        
    def check_main_vars(self):
        if self.unit_name.get() == '':
            return (False, '\n\nERROR: please make sure you have entered a unit ID abbreviation.')

        if self.shipment_date.get() == '':
            return (False, '\n\nERROR: please make sure you have entered a shipment date.')
        
        #check barcode value, too, if we're using standard BDPL Ingest tab
        if self.get_current_tab() == 'BDPL Ingest':
            if not os.path.exists(self.bdpl_work_dir):
                self.connect_to_server("bdpl_workspace")
            
            if self.item_barcode.get() == '':
                return (False, '\n\nERROR: please make sure you have entered a barcode value.')
                
        #if RipStation job, make sure essential info/files are identified
        elif self.get_current_tab() == 'RipStation Ingest':
            if not os.path.exists(self.bdpl_work_dir):
                self.connect_to_server("bdpl_workspace")
            
            if not os.path.exists(self.ripstation_log.get()):
                return (False, '\n\nERROR: select RipStation log file before continuing')
            
            if not os.path.exists(self.ripstation_userdata.get()):
                return (False, '\n\nERROR: select RipStation userdata.txt file before continuing')
                
            if not self.ripstation_ingest_option.get() in ['CDs', 'DVD_Data']:
                return (False, '\n\nERROR: select RipStation job option before continuing.')
        
        elif self.get_current_tab() == 'Deposit to SDA':
            if not os.path.exists(self.bdpl_archiver_dir):
                self.connect_to_server("bdpl_archiver")
                
        #if we get through the above, then we are good to go!
        return (True, 'Unit name and shipment date included.')
        
    def shipment_status(self):
        current_spreadsheet = Spreadsheet(self)
        current_spreadsheet.check_shipment_progress()
        
    def media_images(self):
        current_unit = Unit(self)  
        current_unit.move_media_images()
        
    def add_manual_premis_event(self): 
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.check_main_vars()
        if not status:
            print(msg)
            return

        #create a manual PREMIS object
        new_premis_event = ManualPremisEvent(self)   
        
    def update_combobox(self, combobox):
        if self.unit_name.get() == '':
            combobox_list = []
        else:
            unit_home = os.path.join(self.bdpl_work_dir, self.unit_name.get(), 'ingest')
            combobox_list = glob.glob1(unit_home, '*')

        combobox['values'] = combobox_list
        
    def clear_gui(self):        
        
        newscreen()
        
        #reset all text fields/labels        
        self.content_source_type.set('')
        self.collection_title.set('')
        self.collection_creator.set('')
        self.item_title.set('')
        self.label_transcription.set('')
        self.item_description.set('')
        self.appraisal_notes.set('')
        self.bdpl_instructions.set('')
        self.item_barcode.set('')
        self.path_to_content.set('')
        self.other_device.set('')
        
        self.ripstation_log.set('')
        self.ripstation_userdata.set('')
        
        #reset 5.25" floppy disk type
        self.disk_525_type.set('N/A')
        
        #reset checkbuttons
        self.bdpl_failure_notification.set(False)
        self.re_analyze.set(False)
        self.media_attached.set(False)
        self.separations_status.set(False)
        
        #reset radio buttons
        self.job_type.set(None)
        self.source_device.set(None)
        self.ripstation_ingest_option.set(None)
        
        #reset note text box
        self.tabs['BdplIngest'].bdpl_technician_note.delete(1.0, tk.END)
        
        if self.get_current_tab() == 'RipStation Ingest':
            self.unit_name.set('')
            self.shipment_date.set('')
        
    def connect_to_server(self, servername):
        connect_dialogue = ServerConnect(self, servername)
         
    def check_list(self, list_name, item_barcode):
        if not os.path.exists(list_name):
            return False
        with open(list_name, 'r') as f:
            for item in f:
                if item_barcode in item.strip():
                    return True
                else:
                    continue
            return False
            
    def write_list(self, list_name, message):
        with open(list_name, 'a') as f:
            f.write('%s\n' % message)

class ServerConnect(tk.Toplevel):
    def __init__(self, controller, servername):
        tk.Toplevel.__init__(self, controller)
        self.title('BDPL Ingest: Connect to Server')
        self.iconbitmap(r'C:/BDPL/scripts/favicon.ico')
        self.protocol('WM_DELETE_WINDOW', self.close_top)
        
        self.servername = servername
        self.server = tk.StringVar()
        self.drive_letter = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        
        self.controller = controller
        
        with open(self.controller.addresses, 'r') as f:
            servers = f.read().splitlines()
            
        if self.servername == 'bdpl_workspace':
            self.server.set(servers[0])
            self.drive_letter.set('Z:')
        elif self.servername == 'bdpl_archiver':
            self.server.set(servers[1])
            self.drive_letter.set('W:')
            
        '''
        CREATE FRAMES!
        '''
        tab_frames_list = [('message_frame', ''), ('login_frame', 'Login Information:'), ('button_frame', 'Actions:')]

        self.tab_frames_dict = {}

        for name_, label_ in tab_frames_list:
            f = tk.LabelFrame(self, text = label_)
            f.pack(fill=tk.BOTH, expand=True, pady=5)
            self.tab_frames_dict[name_] = f
        
        '''
        MESSAGE
        '''     
        ttk.Label(self.tab_frames_dict['message_frame'], text='Log in to {}'.format(self.server.get())).pack(padx=10, pady=10)
        
        '''
        LOGIN FIELDS
        '''
        entry_fields = [('Username:', self.username), ('Password:', self.password)]
        
        c = 0
        for label_, var in entry_fields:
            l = tk.Label(self.tab_frames_dict['login_frame'], text=label_, anchor='e', justify=tk.RIGHT, width=10)
            l.grid(row = c, column=0, padx=(10,0), pady=10)
            e = ttk.Entry(self.tab_frames_dict['login_frame'], width=30, textvariable=var)
            if label_ == 'Password:':
                e.config(show='*')
            e.grid(row = c, column=1, padx=(0,10), pady=10)
            c+=1
        
        '''
        BUTTONS
        '''
        button_id = {}
        buttons = ['Connect', 'Cancel']

        for b in buttons:
            button = tk.Button(self.tab_frames_dict['button_frame'], text=b, bg='light slate gray', width = 10)
            button.pack(side=tk.LEFT, padx=25, pady=10)
            button_id[b] = button
        
        button_id['Connect'].config(command=self.login)
        button_id['Cancel'].config(command=self.close_top)
    
    def login(self):
        
        status, mapped_drive = self.check_connection()
        if status:
            if mapped_drive == self.drive_letter.get():
                messagebox.showinfo(title='Already connected', message='{} already mapped to drive {}'.format(self.server.get(), self.drive_letter.get()))
                return
            else:
                messagebox.showwarning(title='WARNING', message='{} is currently mapped to {} drive.\n\nDisconnect and then rerun procedure to map to {} drive.'.format(self.server.get(), mapped_drive, self.drive_letter.get()))      
        
        cmd = 'NET USE {} {} /user:ads\{} "{}"'.format(self.drive_letter.get(), self.server.get(), self.username.get(), self.password.get())
        
        p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        print(p.returncode)
        
        if p.returncode == 0:
            messagebox.showinfo(title='SUCCESS', message='Successfully mapped {} to drive {}'.format(self.server.get(), self.drive_letter.get()))
        else:
            messagebox.showerror(title='ERROR', message='Failed to connect to {}:\n\n{}'.format(self.server.get(), p.stderr))            
    
    def check_connection(self):
        
        cmd = 'net use'
        
        p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        drive_list = p.stdout.splitlines()
        
        found = False
        mapped_drive = ''
        
        for line in drive_list:
            if not line.startswith('OK'):
                continue
            if self.server.get() == line.split()[2]:
                mapped_drive = line.split()[1]
                found = True
                break
        
        return (found, mapped_drive)
    
    def close_top(self):
        #close window
        self.destroy() 

class BdplIngest(tk.Frame):
    def __init__(self, parent, controller):

        #create main frame in notebook
        tk.Frame.__init__(self, parent)
        self.config(height=700)
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
                self.date_combobox = ttk.Combobox(self.tab_frames_dict['batch_info_frame'], width=20, textvariable=var_, postcommand = lambda: self.controller.update_combobox(self.date_combobox))
                self.date_combobox.pack(padx=10, pady=10, side=tk.LEFT)
            else:
                ttk.Label(self.tab_frames_dict['batch_info_frame'], text=label_).pack(padx=(20,0), pady=10, side=tk.LEFT)
                e = ttk.Entry(self.tab_frames_dict['batch_info_frame'], width=width_, textvariable=var_)
                e.pack(padx=10, pady=10, side=tk.LEFT)

        #set up the job type frame
        radio_buttons = [('Copy only', 'Copy_only'), ('Disk Image', 'Disk_image'), ('DVD', 'DVD'), ('CDDA', 'CDDA')]
        
        self.controller.job_type.set(None)
        
        for k, v in radio_buttons:
            ttk.Radiobutton(self.tab_frames_dict['job_type_frame'], text = k, variable = self.controller.job_type, value = v, command = self.set_jobtype_options).pack(side=tk.LEFT, padx=30, pady=5)

        self.re_analyze_chkbx = ttk.Checkbutton(self.tab_frames_dict['job_type_frame'], text='Rerun analysis?', variable=self.controller.re_analyze)
        self.re_analyze_chkbx.pack(side=tk.LEFT, padx=25, pady=5)

        '''
        PATH FRAME: entry box to display directory path and button to launch askfiledialog
        '''
        self.source_entry = ttk.Entry(self.tab_frames_dict['path_frame'], width=80, textvariable=self.controller.path_to_content)
        self.source_entry.pack(side=tk.LEFT, padx=(20,5), pady=5)

        self.source_button = tk.Button(self.tab_frames_dict['path_frame'], text='Browse', bg='light slate gray', command=self.source_browse)
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
        buttons = ['New', 'Load', 'Transfer', 'Analyze', 'Quit']

        for b in buttons:
            button = tk.Button(self.tab_frames_dict['button_frame'], text=b, bg='light slate gray', width = 10)
            button.pack(side=tk.LEFT, padx=25, pady=10)

            button_id[b] = button

        #now use button instances to assign commands
        button_id['New'].config(command = self.controller.clear_gui)
        button_id['Load'].config(command = self.launch_session)
        button_id['Transfer'].config(command = self.launch_transfer)
        button_id['Analyze'].config(command = self.launch_analysis)
        button_id['Quit'].config(command = lambda: close_app(self.controller))

        '''
        BDPL NOTE FRAME: text widget to record notes on the transfer/analysis process.  Also checkbox to document item failure
        '''
        self.bdpl_technician_note = tk.Text(self.tab_frames_dict['bdpl_note_frame'], height=2, width=60, wrap = 'word')
        self.bdpl_note_scroll = ttk.Scrollbar(self.tab_frames_dict['bdpl_note_frame'], orient = tk.VERTICAL, command=self.bdpl_technician_note.yview)

        self.bdpl_technician_note.config(yscrollcommand=self.bdpl_note_scroll.set)

        self.bdpl_technician_note.grid(row=0, column=0, padx=(30, 0), pady=10)
        self.bdpl_note_scroll.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky='ns')

        tk.Button(self.tab_frames_dict['bdpl_note_frame'], text="Save", width=5, bg='light slate gray', command=self.write_technician_note).grid(row=0, column=2, padx=10)

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

        selected_dir = filedialog.askdirectory(parent=self.parent, initialdir=self.controller.bdpl_work_dir, title='Please select the source directory')

        if len(selected_dir) > 0:
            self.controller.path_to_content.set(selected_dir)

    def set_jobtype_options(self):

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

    def launch_session(self):
        #Standard BDPL Ingest item-based workflow
        
        newscreen()
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return

        #create a barcode object and a spreadsheet object
        current_barcode = ItemBarcode(self.controller)
        
        status, msg = current_barcode.prep_barcode()
        if not status:
            print(msg)
            return
            
        #check status
        current_barcode.check_barcode_status()
        
        print('\n\nRecord loaded successfully; ready for next operation.')
    
    def launch_transfer(self):
    
        print('\n\nSTEP 1. TRANSFER CONTENT')

        #create a barcode object and job object
        current_barcode = ItemBarcode(self.controller)

        #make sure transfer details have been correctly entered
        status, msg = current_barcode.verify_transfer_details()
        if not status:
            print(msg)
            return
        
        current_barcode.run_item_transfer()
    
    def launch_analysis(self):
        
        print('\n\nSTEP 2. CONTENT ANALYSIS')
        
        #create a barcode object
        current_barcode = ItemBarcode(self.controller)
        
        #make sure transfer details have been correctly entered
        status, msg = current_barcode.verify_analysis_details()
        if not status:
            print(msg)
            return
            
        #run analysis on item
        current_barcode.run_item_analysis()
    
    def write_technician_note(self):
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #create a barcode object and a spreadsheet object
        current_barcode = ItemBarcode(self.controller)

        current_barcode.metadata_dict['technician_note'] = self.controller.tabs['BdplIngest'].bdpl_technician_note.get(1.0, tk.END)
        
        #additional steps if we are noting failed transfer of item...
        if self.controller.bdpl_failure_notification.get():
            current_barcode.metadata_dict['migration_date'] = str(datetime.datetime.now())
            current_barcode.metadata_dict['migration_outcome'] = "Failure"
            
            done_file = os.path.join(current_barcode.temp_dir, 'done.txt')
            if not os.path.exists(done_file):
                open(done_file, 'a').close()
        
        #save our metadata, just in case...
        current_barcode.pickle_dump('metadata_dict', current_barcode.metadata_dict)
        
        #write info to spreadsheet.  Create a spreadsheet object, make sure spreadsheet isn't already open, and if OK, proceed to open and write info.
        current_spreadsheet = Spreadsheet(self.controller)
        if current_spreadsheet.already_open():
            print('\n\nWARNING: {} is currently open.  Close file before continuing and/or contact digital preservation librarian if other users are involved.'.format(current_spreadsheet.spreadsheet))
            return
            
        current_spreadsheet.open_wb()
        current_spreadsheet.write_to_spreadsheet(current_barcode.metadata_dict)
        
        print('\n\nInformation saved to Appraisal worksheet.') 
  
class RipstationIngest(tk.Frame):
    def __init__(self, parent, controller):

        #create main frame in notebook
        tk.Frame.__init__(self, parent)
        self.config(height=300)
        self.pack(fill=tk.BOTH, expand=True)

        self.parent = parent
        self.controller = controller

        '''
        CREATE FRAMES!
        '''
        tab_frames_list = [('batch_info_frame', 'Basic Information:'), ('job_type_frame', 'Select Job Type:'), ('path_frame', 'Path to RipStation log and userdata.txt files:'), ('button_frame', 'BDPL RipStation Ingest Actions:')]

        self.tab_frames_dict = {}

        for name_, label_ in tab_frames_list:
            f = tk.LabelFrame(self, text = label_)
            f.pack(fill=tk.BOTH, expand=True, pady=5)
            self.tab_frames_dict[name_] = f

        '''
        BATCH INFORMATION FRAME: includes entry fields to capture unit and shipment date
        '''
        entry_fields = [('Unit:', self.controller.unit_name), ('Shipment date:', self.controller.shipment_date)]

        ttk.Label(self.tab_frames_dict['batch_info_frame'], text='Unit:').pack(padx=(20,0), pady=10, side=tk.LEFT)
        e = ttk.Entry(self.tab_frames_dict['batch_info_frame'], width=5, textvariable=self.controller.unit_name)
        e.pack(padx=10, pady=10, side=tk.LEFT)
        
        ttk.Label(self.tab_frames_dict['batch_info_frame'], text='Shipment date:').pack(padx=(20,0), pady=10, side=tk.LEFT)
        self.date_combobox = ttk.Combobox(self.tab_frames_dict['batch_info_frame'], width=20, textvariable=self.controller.shipment_date, postcommand = lambda: self.controller.update_combobox(self.date_combobox))
        self.date_combobox.pack(padx=10, pady=10, side=tk.LEFT)
            
        '''
        RIPSTATION JOB OPTIONS FRAME
        '''
        radio_buttons = [('Compact Disc Digital Audio', 'CDs'), ('DVD/Data discs', 'DVD_Data')]
        
        self.controller.ripstation_ingest_option.set(None)
        
        for k, v in radio_buttons:
            ttk.Radiobutton(self.tab_frames_dict['job_type_frame'], text = k, variable = self.controller.ripstation_ingest_option, value = v).pack(side=tk.LEFT, padx=40, pady=5)
        
        '''
        LOG FILE / USERDATA PATH FRAME: entry box to display directory path and button to launch askfiledialog
        '''
        button_id = {}
        r = 0
        for name, var in {'Log file:' : self.controller.ripstation_log, 'userdata.txt:' : self.controller.ripstation_log}.items():
        
            ttk.Label(self.tab_frames_dict['path_frame'], width=10, text=name, anchor='e', justify=tk.RIGHT).grid(row=r, column=0, padx=(20, 5), pady=5)
            
            e = ttk.Entry(self.tab_frames_dict['path_frame'], width=60, textvariable=var)
            e.grid(row=r, column=1, padx=(5, 20), pady=5)

            b = tk.Button(self.tab_frames_dict['path_frame'], text='Browse', bg='light slate gray')
            b.grid(row=r, column=2, padx=(5, 20), pady=5)
            
            button_id[name] = b
            
            r+=1
        
        button_id['Log file:'].config(command=self.log_browse)
        button_id['userdata.txt:'].config(command=self.userdata_browse)
        
        '''
        BUTTON FRAME: buttons for BDPL RipStation Ingest actions
        '''
        button_id = {}
        buttons = ['New', 'Launch Batch', 'Quit']

        for b in buttons:
            button = tk.Button(self.tab_frames_dict['button_frame'], text=b, bg='light slate gray', width = 15)
            button.pack(side=tk.LEFT, padx=20, pady=10)

            button_id[b] = button

        #now use button instances to assign commands
        button_id['New'].config(command = self.controller.clear_gui)
        button_id['Launch Batch'].config(command = self.launch_ripstation_session)
        button_id['Quit'].config(command = lambda: close_app(self.controller))
            
    def log_browse(self):
        
        current_shipment = Shipment(self.controller)
        
        if os.path.exists(current_shipment.ship_dir):
            target_dir = current_shipment.ship_dir
        else:
            target_dir = self.controller.bdpl_work_dir
        
        self.controller.ripstation_log = filedialog.askopenfilename(parent=self, initialdir=target_dir, title='Select RipStation log file')
        
    def userdata_browse(self):
        
        current_shipment = Shipment(self.controller)
        
        if os.path.exists(current_shipment.ship_dir):
            target_dir = current_shipment.ship_dir
        else:
            target_dir = self.controller.bdpl_work_dir
        
        self.controller.ripstation_userdata = filedialog.askopenfilename(parent=self, initialdir=target_dir, title='Select RipStation userdata.txt file')
        
    def launch_ripstation_session(self):
        
        #must check variables before we create a batch object
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #make sure we have our shipment spreadsheet
        status, msg = Shipment(self.controller).verify_spreadsheet
        if not status:
            print(msg)
            return
        
        #set up Batch object, create folder
        current_batch = RipstationBatch(self.controller)
        current_batch.set_up()
        
        current_batch.ripstation_batch_ingest()

class SdaDeposit(tk.Frame):
    def __init__(self, parent, controller):

        #create main frame in notebook
        tk.Frame.__init__(self, parent)
        self.config(height=300)
        self.pack(fill=tk.BOTH, expand=True)

        self.parent = parent
        self.controller = controller
        self.bdpl_archiver_dir = self.controller.bdpl_archiver_dir
        
        '''
        CREATE FRAMES
        '''
        tab_frames_list = [('batch_info_frame', 'Basic Information:'), ('separations_frame', 'Path to separations.txt (if needed):'), ('button_frame', 'SDA Deposit Actions:')]

        self.tab_frames_dict = {}

        for name_, label_ in tab_frames_list:
            f = tk.LabelFrame(self, text = label_)
            f.pack(fill=tk.BOTH, expand=True, pady=5)
            self.tab_frames_dict[name_] = f
        
        '''
        BATCH INFORMATION FRAME: includes entry fields to capture unit and shipment date
        '''
        entry_fields = [('Unit:', self.controller.unit_name), ('Shipment date:', self.controller.shipment_date)]

        ttk.Label(self.tab_frames_dict['batch_info_frame'], text='Unit:').pack(padx=(20,0), pady=10, side=tk.LEFT)
        e = ttk.Entry(self.tab_frames_dict['batch_info_frame'], width=5, textvariable=self.controller.unit_name)
        e.pack(padx=10, pady=10, side=tk.LEFT)
        
        ttk.Label(self.tab_frames_dict['batch_info_frame'], text='Shipment date:').pack(padx=(20,0), pady=10, side=tk.LEFT)
        self.date_combobox = ttk.Combobox(self.tab_frames_dict['batch_info_frame'], width=20, textvariable=self.controller.shipment_date, postcommand = lambda: self.controller.update_combobox(self.date_combobox))
        self.date_combobox.pack(padx=10, pady=10, side=tk.LEFT)
        
        '''
        SEPARATIONS FRAME
        '''
        self.controller.separations_status.set(False)
        self.separations_chkbx = tk.Checkbutton(self.tab_frames_dict['separations_frame'], text='Content will be separated from shipment?', variable=self.controller.separations_status, command = self.separations_check, anchor='w', justify=tk.LEFT)
        self.separations_chkbx.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        self.separations_file = ttk.Entry(self.tab_frames_dict['separations_frame'], width=80, )
        self.separations_file.grid(row=1, column=0, padx=10, pady=10)
        self.separations_file['state'] = 'disabled'

        tk.Button(self.tab_frames_dict['separations_frame'], text='Add file', bg='light slate gray', command=self.separations_browse).grid(row=1, column=1, padx=10, pady=10)
        
        '''
        BUTTON FRAME
        '''
        
        tk.Button(self.tab_frames_dict['button_frame'], text='Launch Deposit', width=15, bg='light slate gray', command=self.launch_sda_deposit).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.tab_frames_dict['button_frame'], text='Quit', width=15, bg='light slate gray', command = lambda: close_app(self.controller)).grid(row=0, column=2, padx=10, pady=10)
        self.tab_frames_dict['button_frame'].grid_columnconfigure(0, weight=1)
        self.tab_frames_dict['button_frame'].grid_columnconfigure(3, weight=1)
        
    def separations_check(self):
        if self.controller.separations_status.get():
            self.separations_file['state'] = '!disabled'
        else:
            self.separations_file['state'] = 'disabled'
            
    def separations_browse(self):
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        current_shipment = Shipment(self.controller)
        
        if os.path.exists(current_shipment.ship_dir):
            target_dir = current_shipment.ship_dir
        else:
            target_dir = self.controller.bdpl_work_dir
        
        sep_file = filedialog.askopenfilename(parent=self, initialdir=target_dir, title='Select separations.txt')
        
        self.separations_file.set(sep_file)
        
    def launch_sda_deposit(self):
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
            
        print('Launching!')      

def close_app(window):
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
        print('Missing ASCII art header file; download to: {}'.format(fname))

def update_software():
    #make sure PRONOM and antivirus signatures are up to date
    sfup = 'sf -update'
    fresh_up = 'freshclam'
    droid_up = 'droid -d'
    
    update_completed = 'C:/BDPL/resources/clamav/updated.txt'

    #don't run update if we've already completed one today
    if os.path.exists(update_completed):
        file_mod_time = datetime.datetime.fromtimestamp(os.stat(update_completed).st_mtime).strftime('%Y%m%d')
    else:
        file_mod_time = datetime.datetime.strptime('20200101', '%Y%m%d').strftime('%Y%m%d')
        
    now = datetime.datetime.today().strftime('%Y%m%d')
    
    if now > file_mod_time:
        print('\n\nUpdating PRONOM and antivirus signatures...')
        
        subprocess.check_output(sfup, shell=True, text=True)
        subprocess.check_output(droid_up, shell=True, text=True)
        output = subprocess.run(fresh_up, shell=True, text=True, capture_output=True)
        
        #if clamav is outdated, update it
        if 'OUTDATED!' in output.stderr:
            version = output.stderr.strip().split('Recommended version: ')[1]
            update_clamav(version)
        
        print('\nUpdate complete!  Time to ingest some date...')
        
        open(update_completed, 'w').close()
    
def close_app(window):
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
        print('Missing ASCII art header file; download to: {}'.format(fname))

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    try:
        speed = int(progress_size / (1024 * duration))
    except ZeroDivisionError:
        speed = int(progress_size / (1024 * 1))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r\t...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def update_clamav(version):
    
    print('\nUpdating ClamAV...')
    
    download = "https://www.clamav.net/downloads/production/clamav-{}-win-x64-portable.zip".format(version)

    print('\n\tChecking {}...'.format(download))

    #make sure the URL works; exit if not.  NOTE: may need to change hard-coded URL
    try:
        urllib.request.urlopen(download)
        print('\n\tURL looks good...')
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(e, '\n\n{} URL may be incorrect; inform digital preservation librarian that manual installation may be required.')
        return

    filename = os.path.basename(download)

    #get username so we can download to local Downloads folder
    username = os.getlogin()
    downloads = os.path.join('C:\\Users', username, 'Downloads')
    dest = os.path.join(downloads, filename)

    if os.path.exists(dest):
        os.remove(dest)

    #download zip file
    print('\n\tDownloading new version of ClamAV...\n')
    urllib.request.urlretrieve(download, dest, reporthook)

    #extract contents of zip
    print('\n\tExtracting contents from zip file...')
    extract_dest = os.path.join(downloads, 'clamav')
    if os.path.exists(extract_dest):
        shutil.rmtree(extract_dest)
        
    with zipfile.ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(extract_dest)
        
    #copy our freshclam.conf file
    conf_file = 'C:/BDPL/resources/clamav/freshclam.conf'
    if os.path.exists(conf_file):
        shutil.copy('C:/BDPL/resources/clamav/freshclam.conf', extract_dest)

    #remove old clamav
    print('\n\tRemoving old version of ClamAV...')
    bdpl_dest = 'C:/BDPL/resources/clamav'
    if os.path.exists(bdpl_dest):
        shutil.rmtree(bdpl_dest)

    #create new conf files if they don't exist:
    if not os.path.exists(os.path.join(extract_dest, 'freshclam.conf')):
        shutil.copy(os.path.join(extract_dest, 'conf_examples', 'freshclam.conf.sample'),  os.path.join(extract_dest, 'freshclam.conf'))
        shutil.copy(os.path.join(extract_dest, 'conf_examples', 'clamd.conf.sample'),  os.path.join(extract_dest, 'clamd.conf'))
        
    #copy over new version
    print('\n\tMoving new version to {}...'.format(bdpl_dest))
    shutil.move(extract_dest, 'C:/BDPL/resources')

    #run freshclam to update definitions
    print('\n\tUpdating antivirus definitions...\n')
    subprocess.check_output('freshclam', shell=True, text=True)
    
    print('\n\tClamAV update complete!')

def main():
    #clear CMD.EXE screen and print logo
    newscreen()
    
    if not os.path.exists('C:/BDPL/resources/addresses.txt'):
        print('\n\nWARNING: missing file with Scandium UNC paths.  Add file at: C:/BDPL/resources/addresses.txt and restart application.')
        
        stop_ = input('Hit enter to close application:')
        sys.exit(0)
    
    update_software()

    #assign path for 'home directory'.  Change if needed...
    bdpl_work_dir = 'Z:\\'
    bdpl_archiver_dir = 'W:\\'

    #create and launch our main app.
    bdpl = BdplMainApp(bdpl_work_dir, bdpl_archiver_dir)
    bdpl.mainloop()

if __name__ == "__main__":
    main()
