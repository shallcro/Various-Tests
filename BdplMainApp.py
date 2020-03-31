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

#BDPL files
from BdplObjects import Unit, Shipment, ItemBarcode, Spreadsheet
from BdplIngest import BdplIngest

#set up as controller
class BdplMainApp(tk.Tk):
    def __init__(self, bdpl_home_dir):
        tk.Tk.__init__(self)

        self.title("Indiana University Library Born-Digital Preservation Lab")
        self.iconbitmap(r'C:/BDPL/scripts/favicon.ico')
        self.protocol('WM_DELETE_WINDOW', lambda: close_app(self))

        self.bdpl_home_dir = bdpl_home_dir
        self.bdpl_resources = os.path.join(bdpl_home_dir, 'bdpl_resources')
        
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
        app_tabs = {BdplIngest : 'BDPL Ingest'} #, RipstationIngest : 'RipStation Ingest'}

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
        self.actions_.add_command(label='Check shipment status', command=self.check_shipment_progress)
        self.actions_.add_separator()
        self.actions_.add_command(label='Move media images', command=self.move_media_images)
        self.actions_.add_separator()
        self.actions_.add_command(label='Add Manual PREMIS event', command=self.add_manual_premis_event)
        
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
        
    def add_manual_premis_event(self): 
        #make sure main variables--unit_name, shipment_date, and barcode--are included.  Return if either is missing
        status, msg = self.check_main_vars()
        if not status:
            print(msg)
            return

        #create a manual PREMIS object
        new_premis_event = ManualPremisEvent(self)
        
    def move_media_images(self):
        #create unit object
        current_unit = Unit(self)
        
        #make sure unit value is not empty and that 
        if current_unit.unit_name == '':
            '\n\nError; please make sure you have entered a unit ID abbreviation.'
            return 
                
        if len(os.listdir(current_unit.media_image_dir)) == 0:
            print('\n\nNo images of media at {}'.format(current_unit.media_image_dir))
            return
        
        # get a list of barcodes in each shipment
        all_barcode_folders = list(filter(lambda f: os.path.isdir(f), glob.glob('{}\\*\\*'.format(current_unit.unit_home))))

        #list of files with no parent
        bad_file_list = []
        
        #loop through a list of all images in this folder; try to find match in list of barcodes; if not, add to 'bad file list'
        for f in os.listdir(current_unit.media_image_dir):
            pic = f.split('-')[0]
            barcode_folder = [s for s in all_barcode_folders if pic in s]
            if len(barcode_folder) == 1:
                media_pics = os.path.join(barcode_folder[0], 'metadata', 'media-image')
                if not os.path.exists(media_pics):
                    os.makedirs(media_pics)
                try:
                    shutil.move(os.path.join(current_unit.media_image_dir, f), media_pics)
                except shutil.Error as e:
                    print('NOTE: ', e)
                    print('\n\nCheck the media image folder to determine if a file already exists or a filename is being duplicated.')
            else:
                bad_file_list.append(f)
            
        if len(bad_file_list) > 0:
            print('\n\nFilenames for the following images do not match current barcodes:\n{}'.format('\n'.join(bad_file_list)))
            print('\nPlease correct filenames and try again.')
        else:
            print('\n\nMedia images successfully copied!')

    def check_shipment_progress(self):
        #report on how many items have been completed; how many remain to be done
        
        #create a spreadsheet object
        current_spreadsheet = Spreadsheet(self)
        
        #verify unit and shipment_date info has been entered
        if current_spreadsheet.unit_name == '' or current_spreadsheet.shipment_date == '':
            '\n\nError; please make sure you have entered a unit ID abbreviation and shipment date.'
            return 
        
        #verify spreadsheet--make sure we only have 1 & that it follows naming conventions
        status, msg = current_spreadsheet.verify_spreadsheet()
        if not status:
            print(msg)
            return
        
        current_spreadsheet.open_wb()
        
        #get list of all barcodes on appraisal spreadsheet
        app_barcodes = []
        for col in current_spreadsheet.app_ws['A'][1:]:
            if not col.value is None:
                app_barcodes.append(str(col.value))
        
        #get list of all barcodes on inventory spreadsheet
        inv_barcodes = {}
        for col in current_spreadsheet.inv_ws['A'][1:]:
            if not col.value is None:
                inv_barcodes[str(col.value)] = col.row
        
        inv_list = list(inv_barcodes.keys())        
        
        #check to see if there are any duplicate barcodes in the inventory; print warning if so
        duplicate_barcodes = [item for item, count in Counter(inv_list).items() if count > 1]
        
        if duplicate_barcodes:
            print('\n\nWARNING! Inventory contains at least one duplicate barcode:')
            for dup in duplicate_barcodes:
                print('\t{}\tRow: {}'.format(dup, inv_barcodes[dup]))
        
        current_total = len(inv_list) - len(app_barcodes)
        
        items_not_done = list(set(inv_list) - set(app_barcodes))
        
        if len(items_not_done) > 0:
            print('\n\nThe following barcodes require ingest:\n{}'.format('\n'.join(items_not_done)))
        
        print('\n\nCurrent status: {} out of {} items have been ingested. \n\n{} remain.'.format(len(app_barcodes), len(inv_list), current_total))
        
class ManualPremisEvent(tk.Toplevel):
    def __init__(self, controller):
        tk.Toplevel.__init__(self, controller)
        self.title('BDPL Ingest: Add PREMIS Event')
        self.iconbitmap(r'C:/BDPL/scripts/favicon.ico')
        self.protocol('WM_DELETE_WINDOW', self.close_top)
        
        self.controller = controller
        
        #self.db = 
        
        if self.controller.get_current_tab() != 'BDPL Ingest' or self.controller.item_barcode.get()=='':
            self.get_info_frame = tk.Frame(self)
            self.get_info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.l = ttk.Label(self.get_info_frame, text='Enter barcode:', anchor='e', justify=tk.RIGHT, width=25)
            self.l.grid(row=0, column=0, padx=(10,0), pady=10)
            
            self.barcode_entry = tk.Entry(self.get_info_frame, justify=tk.LEFT, width=50)
            self.barcode_entry.grid(row=0, column=1, padx=(0,10), pady=10, sticky='w')
            
            tk.Button(self.get_info_frame, text = 'Use barcode', bg='light slate gray', command=self.add_barcode_value).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            tk.Button(self.get_info_frame, text = 'Cancel', bg='light slate gray', command=self.close_top).grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.barcode_item = ItemBarcode(self.controller)

        self.event_frame = tk.LabelFrame(self, text='Item Barcode: {}'.format(self.controller.item_barcode.get()))
        self.event_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.timestamp_frame = tk.LabelFrame(self, text='Timestamp Information')
        self.timestamp_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.manual_event = tk.StringVar()
        self.manual_event.set('')
        self.manual_event.trace('w', self.update_fields)
        
        self.events = {
            'replication' : 'Created a copy of an object that is, bit-wise, identical to the original.', 
            'disk image creation' : 'Extracted a disk image from the physical information carrier.',
            'forensic feature analysis' : 'Forensically analyzed the disk image raw bitstream',
            'format identification' : 'Determined file format and version numbers for content recorded in the PRONOM format registry.', 
            'message digest calculation' : 'Extracted information about the structure and characteristics of content, including file checksums.',
            'metadata extraction' : 'Extracted metadata from the object.',
            'metadata modification' : 'Corrected file timestamps to match information extracted from disk image.',
            'normalization' : 'Transformed object to an institutionally supported preservation format.',
            'virus check' : 'Scanned files for malicious programs.'
        }
        
        self.current_event = {}
        widgets = {'event_combobox' : 'Select event:', 'event_software' : 'Software name:', 'event_software_version' : 'Version #:', 'event_command' : 'Command / Description:', 'event_description' : 'Describe preservation event:'}
        
        r = 0
        for name_, label_ in widgets.items():
            l = '{}_label'.format(name_)
            self.current_event[l] = ttk.Label(self.event_frame, text=label_, anchor='e', justify=tk.RIGHT, width=25)
            
            if name_ == 'event_combobox':
                self.current_event[name_] = ttk.Combobox(self.event_frame, textvariable=self.manual_event, values=list(self.events.keys()), justify=tk.LEFT, width=30)
                self.current_event[name_].bind("<<ComboboxSelected>>", self.update_fields)
            else:
                self.current_event[name_] = tk.Entry(self.event_frame, justify=tk.LEFT, width=50)
            
            if name_ != 'event_description':
                self.current_event[l].grid(row=r, column=0, padx=(10,0), pady=10)
                self.current_event[name_].grid(row=r, column=1, padx=(0,10), pady=10, sticky='w')               
            r+=1
        
        self.timestamp_source = tk.StringVar()
        self.timestamp_source.set(None)
        
        info = [['Use "now" for timestamp', 'now'], ['Get timestamp from file', 'file'], ['Get timestamp from folder', 'folder']]
        c = 0
        for i in info:
            ttk.Radiobutton(self.timestamp_frame, text = i[0], variable = self.timestamp_source, value = i[1], command=self.get_timestamp).grid(row=c, column=0, padx=10, pady=10, sticky='w')
            c += 1
        
        self.notice = ttk.Label(self.timestamp_frame, text='NOTE: folder contents will be copied to {}'.format(self.barcode_item.files_dir), wraplength=250)
        
        tk.Button(self.button_frame, text = 'Save Event', bg='light slate gray', command=self.create_manual_premis_event).grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        tk.Button(self.button_frame, text = 'Quit / Cancel', bg='light slate gray', command=self.close_top).grid(row=1, column=2, padx=20, pady=10, sticky="nsew")
        
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)
    
    def add_barcode_value(self):
        if self.barcode_entry.get() == '':
            print('\n\nWARNING: Be sure to enter a barcode value')
            return
        else:
            self.controller.item_barcode.set(self.barcode_entry.get().trim())
            
        if not Spreadsheet(self.controller).return_inventory_row()[0]:
            print('\n\nWARNING: Barcode value does not appear in spreadsheet')
            return
        else:
            self.get_info_frame.destroy()
    
    def update_fields(self, *args):
        if self.manual_event.get()=='replication':
            self.notice.grid(row=2, column=1, columnspan = 3, padx=10, pady=10, sticky='w')
        else:
            if self.notice.winfo_ismapped():
                self.notice.grid_forget()
                
        #if user adds a different event, we need to get a description of it.  Add fields.
        if not self.events.get(self.manual_event.get()):
            self.current_event['event_description_label'].grid(row=4, column=0, padx=(10,0), pady=10)
            self.current_event['event_description'].grid(row=4, column=1, columnspan=3, padx=(0,10), pady=10)
        #If the event is already recognized, we don't need to have extra fields.  Hide them if they exist. 
        else:
            if self.current_event['event_description_label'].winfo_ismapped():
                self.current_event['event_description_label'].grid_forget()
                self.current_event['event_description'].grid_forget()
            
    def get_timestamp(self):
        if self.timestamp_source.get() == 'now':
            ts = str(datetime.datetime.now())
            
        elif self.timestamp_source.get() == 'folder':
            self.selected_dir = filedialog.askdirectory(parent=self, initialdir=self.controller.bdpl_home_dir, title='Select a folder to extract timestamp from')
            ts = datetime.datetime.fromtimestamp(os.path.getmtime(self.selected_dir)).isoformat()
            
        elif self.timestamp_source.get() == 'file':
            selected_file = filedialog.askopenfilename(parent=self, initialdir=self.controller.bdpl_home_dir, title='Select a file to extract timestamp from')
            ts = datetime.datetime.fromtimestamp(os.path.getmtime(file_)).isoformat()
        
        self.timestamp = ts
        
    def create_manual_premis_event(self):
    
        if not self.events.get(self.manual_event.get()):
            event_desc = self.current_event['event_description'].get()
        else:
            event_desc = self.events[self.manual_event.get()]
        
        #concatenate software name and version #
        vers = '{} v{}'.format(self.current_event['event_software'].get(), self.current_event['event_software_version'].get())
        
        #save info in our 'premis list' for the item 
        self.barcode_item.record_premis(self.timestamp, self.manual_event.get(), 0, self.current_event['event_command'].get(), event_desc, vers)
        
        #if this is a replication event and we've identified a folder, move the folder.  We will also remove any existing DFXML file
        if self.manual_event.get() == 'replication' and self.timestamp_source.get() == 'folder':
            shutil.move(self.selected_dir, self.barcode_item.files_dir)
            
            if os.path.exists(self.barcode_item.dfxml_output):
                os.remove(self.barcode_item.dfxml_output)
                
        print('\nPreservation action ({}) has been succesfully added to PREMIS metadata.')
        
    def close_top(self):
        #close shelve
        
        #close window
        self.destroy()     
        
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
    
    update_software()

    #assign path for 'home directory'.  Change if needed...
    bdpl_home_dir = 'Z:\\'

    #create and launch our main app.
    bdpl = BdplMainApp(bdpl_home_dir)
    bdpl.mainloop()

if __name__ == "__main__":
    main()
