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
from urllib.parse import unquote
import urllib.request
import uuid
import webbrowser
import zipfile

# from dfxml project
import Objects

from BdplObjects import Unit, Shipment, ItemBarcode, Spreadsheet
from BdplUtilities import *

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
        button_id['New'].config(command = self.clear_gui)
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

        selected_dir = filedialog.askdirectory(parent=self.parent, initialdir=self.controller.bdpl_home_dir, title='Please select the source directory')

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

    def update_combobox(self):
        if self.controller.unit_name.get() == '':
            combobox_list = []
        else:
            unit_home = os.path.join(self.controller.bdpl_home_dir, self.controller.unit_name.get(), 'ingest')
            combobox_list = glob.glob1(unit_home, '*')

        self.date_combobox['values'] = combobox_list

    def launch_session(self):
        newscreen()
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #Standard BDPL Ingest item-based workflow
        if self.controller.get_current_tab() == 'BDPL Ingest':

            #create a barcode object and a spreadsheet object
            current_barcode = ItemBarcode(self.controller)
            current_spreadsheet = Spreadsheet(self.controller)

            #verify spreadsheet--make sure we only have 1 & that it follows naming conventions
            status, msg = current_spreadsheet.verify_spreadsheet()
            if not status:
                print(msg)
                return

            #make sure spreadsheet is not open
            if current_spreadsheet.already_open():
                print('\n\nWARNING: {} is currently open.  Close file before continuing and/or contact digital preservation librarian if other users are involved.'.format(current_spreadsheet.spreadsheet))
                return
                
            #open spreadsheet and make sure current item exists in spreadsheet; if not, return
            current_spreadsheet.open_wb()
            status, row = current_spreadsheet.return_inventory_row()
            if not status:
                print('\n\nWARNING: barcode was not found in spreadsheet.  Make sure value is entered correctly and/or check spreadsheet for value.  Consult with digital preservation librarian as needed.')
                return
            
            #load metadata into item object
            current_barcode.load_item_metadata(current_spreadsheet, row)
            
            #assign variables to GUI
            self.controller.content_source_type.set(current_barcode.metadata_dict['content_source_type'])
            self.controller.collection_title.set(current_barcode.metadata_dict['collection_title'])
            self.controller.collection_creator.set(current_barcode.metadata_dict['collection_creator'])
            self.controller.item_title.set(current_barcode.metadata_dict.get('item_title', '-'))
            self.controller.label_transcription.set(current_barcode.metadata_dict['label_transcription'])
            self.controller.item_description.set(current_barcode.metadata_dict.get('item_description', '-'))
            self.controller.appraisal_notes.set(current_barcode.metadata_dict['appraisal_notes'])
            self.controller.bdpl_instructions.set(current_barcode.metadata_dict['bdpl_instructions'])
            
            #create folders
            if not current_barcode.check_ingest_folders(): 
                current_barcode.create_folders() 
                
            #check status
            current_barcode.check_barcode_status()
            
            print('\n\nRecord loaded successfully; ready for next operation.')
    
    def launch_transfer(self):

        print('\n\nSTEP 1. TRANSFER CONTENT')
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #create a barcode object and job object
        current_barcode = ItemBarcode(self.controller)
        
        #make sure we have already initiated a session for this barcode
        if not current_barcode.check_ingest_folders():
            print('\n\nWARNING: load record before proceeding')
            return
        
        #make sure transfer details have been correctly entered
        status, msg = current_barcode.verify_transfer_details()
        if not status:
            print(msg)
            return
            
        #Copy only job
        if current_barcode.job_type == 'Copy_only':
            current_barcode.secure_copy(current_barcode.path_to_content)
        
        #Disk image job type
        elif current_barcode.job_type == 'Disk_image':
            if current_barcode.source_device == '5.25':
                    current_barcode.fc5025_image()
            else:
                current_barcode.ddrescue_image()
                
            #next, get technical metadata from disk image and replicate files so we can run additional analyses (this step will also involve creating DFXML and correcting MAC times)
            current_barcode.disk_image_info()
            current_barcode.disk_image_replication()
        
        #DVD job
        elif current_barcode.job_type == 'DVD':

            current_barcode.ddrescue_image()
            
            #check DVD for title information
            drive_letter = "{}\\".format(current_barcode.optical_drive_letter())
            titlecount, title_format = current_barcode.lsdvd_check(drive_letter)
            
            #make surre this isn't PAL formatted: need to figure out solution. 
            if title_format == 'PAL':
                print('\n\nWARNING: DVD is PAL formatted! Notify digital preservation librarian so we can configure approprioate ffmpeg command; set disc aside for now...')
                return
            
            #if DVD has one or more titles, rip raw streams to .MPG
            if titlecount > 0:
                current_barcode.normalize_dvd_content(titlecount, drive_letter)
            else:
                print('\nWARNING: DVD does not appear to have any titles; job type should likely be Disk_image.  Manually review disc and re-transfer content if necessary.')
                return
        
        #CDDA job
        elif current_barcode.job_type == 'CDDA':
            #create a copy of raw pulse code modulated (PCM) audio data and then rip to WAV using cd-paranoia
            current_barcode.cdda_image_creation()
            current_barcode.cdda_wav_creation()

        print('\n\n--------------------------------------------------------------------------------------------------\n\n')
    
    def launch_analysis(self):
        
        print('\n\nSTEP 2. CONTENT ANALYSIS')
        
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.controller.check_main_vars()
        if not status:
            print(msg)
            return
        
        #create a barcode object
        current_barcode = ItemBarcode(self.controller)
        
        #make sure we have already initiated a session for this barcode
        if not current_barcode.check_ingest_folders():
            print('\n\nWARNING: load record before proceeding')
            return
        
        #make sure transfer details have been correctly entered
        status, msg = current_barcode.verify_analysis_details()
        if not status:
            print(msg)
            return
            
        '''run antivirus'''
        print('\nVIRUS SCAN: clamscan.exe')
        if current_barcode.check_premis('virus check') and not current_barcode.re_analyze:
            print('\n\tVirus scan already completed; moving on to next step...')
        else:
            current_barcode.run_antivirus()
    
        '''create DFXML (if not already done so)'''
        if current_barcode.check_premis('message digest calculation') and not current_barcode.re_analyze:
            print('\n\nDIGITAL FORENSICS XML CREATION:')
            print('\n\tDFXML already created; moving on to next step...')
        else:
            if current_barcode.job_type == 'Disk_image':
                #DFXML creation for disk images will depend on the image's file system; check fs_list
                fs_list = current_barcode.pickle_load('ls', 'fs_list')
                
                #if it's an HFS+ file system, we can use fiwalk on the disk image; otherwise, use bdpl_ingest on the file directory
                if 'hfs+' in [fs.lower() for fs in fs_list]:
                    current_barcode.produce_dfxml(current_barcode.imagefile)
                else:
                    current_barcode.produce_dfxml(current_barcode.files_dir)
            
            elif current_barcode.job_type == 'Copy_only':
                current_barcode.produce_dfxml(current_barcode.files_dir)
            
            elif current_barcode.job_type == 'DVD':
                current_barcode.produce_dfxml(current_barcode.imagefile)
            
            elif current_barcode.job_type == 'CDDA':
                current_barcode.produce_dfxml(current_barcode.image_dir)
                
            '''document directory structure'''
            print('\n\nDOCUMENTING FOLDER/FILE STRUCTURE: TREE')
            if current_barcode.check_premis('metadata extraction') and not current_barcode.re_analyze:
                print('\n\tDirectory structure already documented with tree command; moving on to next step...')
            else:
                current_barcode.document_dir_tree() 
        
        '''run bulk_extractor to identify potential sensitive information (only if disk image or copy job type). Skip if b_e was run before'''
        print('\n\nSENSITIVE DATA SCAN: BULK_EXTRACTOR')
        if current_barcode.check_premis('sensitive data scan') and not current_barcode.re_analyze:
            print('\n\tSensitive data scan already completed; moving on to next step...')
        else:
            if current_barcode.job_type in ['Copy_only', 'Disk_image']:
                current_barcode.run_bulkext()
            else:
                print('\n\tSensitive data scan not required for DVD-Video or CDDA content; moving on to next step...')
                
        '''run siegfried to characterize file formats'''
        print('\n\nFILE FORMAT ANALYSIS')
        if current_barcode.check_premis('format identification') and not current_barcode.re_analyze:
            print('\n\tFile format analysis already completed; moving on to next operation...')
        else:
            current_barcode.format_analysis()
        
        #load siegfried.csv into sqlite database; skip if it's already completed
        if not os.path.exists(current_barcode.sqlite_done) or current_barcode.re_analyze:
            current_barcode.import_csv() # load csv into sqlite db
        
        '''generate statistics/reports'''
        if not os.path.exists(self.stats_done) or current_barcode.re_analyze:
            current_barcode.get_stats()
        
        '''write info to HTML'''
        if not os.path.exists(self.new_html) or current_barcode.re_analyze:
            current_barcode.generate_html()
        
        #generate PREMIS preservation metadata file
        current_barcode.print_premis()
        
        #write info to spreadsheet for collecting unit to review.  Create a spreadsheet object, make sure spreadsheet isn't already open, and if OK, proceed to open and write info.
        current_spreadsheet = Spreadsheet(self.controller)
        
        if current_spreadsheet.already_open():
            print('\n\nWARNING: {} is currently open.  Close file before continuing and/or contact digital preservation librarian if other users are involved.'.format(current_spreadsheet.spreadsheet))
            return
        
        current_spreadsheet.open_wb()
        current_spreadsheet.write_to_spreadsheet(current_barcode.metadata_dict)
           
        #create file to indicate that process was completed
        done_file = os.path.join(current_barcode.temp_dir, 'done.txt')
        if not os.path.exists(done_file):
            open(done_file, 'a').close()
            
        #copy in .CSS and .JS files for HTML report
        if os.path.exists(current_barcode.assets_target):
            pass
        else:
            shutil.copytree(current_barcode.assets_dir, current_barcode.assets_target)
        
        '''clean up; delete disk image folder if empty and remove temp_html'''
        try:
            os.rmdir(current_barcode.image_dir)
        except (WindowsError, PermissionError):
            pass

        # remove temp html file
        try:
            os.remove(os.path.join(current_barcode.temp_dir, 'temp.html'))
        except WindowsError:
            pass
        
        '''if using gui, print final details about item'''
        if self.controller.get_current_tab() == 'BDPL Ingest':
            print('\n\n--------------------------------------------------------------------------------------------------\n\nINGEST PROCESS COMPLETED FOR ITEM {}\n\nResults:\n'.format(current_barcode.item_barcode))
            
            final_stats = os.path.join(current_barcode.temp_dir, 'final_stats.txt')
            du_cmd = 'du64.exe -nobanner "{}" > {}'.format(current_barcode.files_dir, final_stats)
            
            subprocess.call(du_cmd, shell=True, text=True)   
            
            if os.path.exists(current_barcode.image_dir):
                di_count = len(os.listdir(current_barcode.image_dir))
                if di_count > 0:
                    print('Disk Img(s):   {}'.format(di_count))
            du_list = ['Files:', 'Directories:', 'Size:', 'Size on disk:']
            with open(final_stats, 'r') as f:
                for line, term in zip(f.readlines(), du_list):
                    if "Directories:" in term:
                        print(term, ' ', str(int(line.split(':')[1]) - 1).rstrip())
                    else: 
                        print(term, line.split(':')[1].rstrip())
            print('\n\nReady for next item!') 
    
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
        self.bdpl_technician_note.delete(1.0, tk.END)