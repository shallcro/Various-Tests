from tkinter import *
from tkinter import ttk

window = Tk()
window.title("Indiana University Library Born-Digital Preservation Lab")
#window.geometry('650x750')

#if user tries to use 'X' button, make sure program closes correctly
#window.protocol('WM_DELETE_WINDOW', lambda: closeUp(window))

'''

GUI section for barcode, shipment, and unit info

'''

topFrame = Frame(window, width=650, height=50)
topFrame.pack(fill=BOTH)    

#Get unit name and barcode; provide dynamically updated drop-down to select shipment              
barcode = StringVar()
barcode.set('')           
barcodeTxt = Label(topFrame, text="Barcode:")
barcodeTxt.pack(in_=topFrame, side=LEFT, padx=(10,0), pady=10)
barcodeEntry = Entry(topFrame, width=20, textvariable=barcode)
barcodeEntry.pack(in_=topFrame, side=LEFT, padx=(0,10), pady=10)

unit = StringVar()
unit.set('')
unitTxt = Label(topFrame, text="Unit:")
unitTxt.pack(in_=topFrame, side=LEFT, padx=(10,0), pady=10)
unitEntry = Entry(topFrame, width=5, textvariable=unit)
unitEntry.pack(in_=topFrame, side=LEFT, padx=(0,10), pady=10)

shipLabel = Label(topFrame, text="Shipment ID: ")
shipLabel.pack(in_=topFrame, side=LEFT, padx=(10,0), pady=10)

#User can either select an existng shipment date or add new one
#global unit_shipment_date
this_date = StringVar()
unit_shipment_date = Entry(topFrame, width=20, textvariable = this_date)
unit_shipment_date.pack(in_=topFrame, side=LEFT, padx=(0,10), pady=10)

#alternative approach: text entry
# unit_shipment_date= StringVar()
# unit_shipment_date.set('')
# shipmentDateEntry = Entry(topFrame, width=10, textvariable=unit_shipment_date)
# shipmentDateEntry.pack(in_=topFrame, side=LEFT, padx=5, pady=5)

'''

GUI section for job info

'''

middleFrame = Frame(window, width=650, height=150)
middleFrame.pack(fill=BOTH)
middleFrame.pack_propagate(False)

'''
            UPPER MIDDLE
'''

upperMiddle = Frame(middleFrame, width=650, height=50)
upperMiddle.pack(fill=BOTH)

#job types: these determine which operations run on content
jobTypeLabel = Label(upperMiddle, text="Job type:")
jobTypeLabel.grid(column=0, row=1, padx=5, pady=5)

jobType = StringVar()
jobType.set(None)

jobType1 = Radiobutton(upperMiddle, text='Copy only', value='Copy_only', variable=jobType)                     
jobType1.grid(column=1, row=1, padx=15, pady=5)

jobType2 = Radiobutton(upperMiddle, text='Disk image', value='Disk_image', variable=jobType)
jobType2.grid(column=2, row=1, padx=15, pady=5)

jobType3 = Radiobutton(upperMiddle, text='DVD', value='DVD', variable=jobType)
jobType3.grid(column=3, row=1, padx=15, pady=5)

jobType4 = Radiobutton(upperMiddle, text='CDDA', value='CDDA', variable=jobType)
jobType4.grid(column=4, row=1, padx=15, pady=5)

re_analyze = BooleanVar()
re_analyze.set(False)
re_analyzeChk = Checkbutton(upperMiddle, text='Re-analyze files', variable=re_analyze)
re_analyzeChk.grid(column=5, row=1, padx=15, pady=5)

'''
            MID MIDDLE
'''
midMiddle = Frame(middleFrame, width=650, height=25)
midMiddle.pack(fill=BOTH)

#Get path to source, if needed
source = StringVar()
source.set('')
sourceTxt = Label(midMiddle, text='Source / file list\n("COPY" only): ')
sourceTxt.pack(in_=midMiddle, side=LEFT, padx=5, pady=5)
sourceEntry = Entry(midMiddle, width=55, textvariable=source)
sourceEntry.pack(in_=midMiddle, side=LEFT, padx=5, pady=5)
sourceBtn = Button(midMiddle, text="Browse", command= lambda: source_browse(window, source))
sourceBtn.pack(in_=midMiddle, side=LEFT, padx=5, pady=5)

'''
        LOWER MIDDLE
'''
lowerMiddle = Frame(middleFrame, width=650, height=100)
lowerMiddle.pack(fill=BOTH)

lowerMiddle1 = Frame(lowerMiddle, width=650, height=25)
lowerMiddle1.pack(fill=BOTH)
lowerMiddle2 = Frame(lowerMiddle, width=650, height=75)
lowerMiddle2.pack(fill=BOTH)
 
#Get source device, if needed
sourceDevice = StringVar()
sourceDevice.set(None)

disk_type_options = ['N/A', 'Apple DOS 3.3 (16-sector)', 'Apple DOS 3.2 (13-sector)', 'Apple ProDOS', 'Commodore 1541', 'TI-99/4A 90k', 'TI-99/4A 180k', 'TI-99/4A 360k', 'Atari 810', 'MS-DOS 1200k', 'MS-DOS 360k', 'North Star MDS-A-D 175k', 'North Star MDS-A-D 350k', 'Kaypro 2 CP/M 2.2', 'Kaypro 4 CP/M 2.2', 'CalComp Vistagraphics 4500', 'PMC MicroMate', 'Tandy Color Computer Disk BASIC', 'Motorola VersaDOS']

disk525 = StringVar()
disk525.set('N/A')
        
sourceDeviceLabel = Label(lowerMiddle1, text='Media:')
sourceDeviceLabel.grid(column=0, row=0)
    
source1 = Radiobutton(lowerMiddle1, text='CD/DVD', value='/dev/sr0', variable=sourceDevice)
source2 = Radiobutton(lowerMiddle1, text='3.5" fd', value='/dev/fd0', variable=sourceDevice)
source3 = Radiobutton(lowerMiddle1, text='5.25" fd', value='5.25', variable=sourceDevice)
disk_menu = OptionMenu(lowerMiddle1, disk525, *disk_type_options)    
source4 = Radiobutton(lowerMiddle1, text='Zip', value='Zip', variable=sourceDevice)
source5 = Radiobutton(lowerMiddle1, text='Other', value='Other', variable=sourceDevice)

other_device = StringVar()
other_device.set('')
other_deviceTxt = Label(lowerMiddle1, text="(& name)")
other_deviceEntry = Entry(lowerMiddle1, width=5, textvariable=other_device)

source1.grid(column=1, row=0, padx=5, pady=5)
source2.grid(column=2, row=0, padx=5, pady=5)
source3.grid(column=3, row=0, padx=5, pady=5)
disk_menu.grid(column=4, row=0, padx=5, pady=5)
source4.grid(column=5, row=0, padx=5, pady=5)
source5.grid(column=6, row=0, padx=(5,0), pady=5)
other_deviceTxt.grid(column=7, row=0, padx=(0,5), pady=5)
other_deviceEntry.grid(column=8, row=0, padx=5, pady=5)


#buttons: kick off various functions    
newBtn = Button(lowerMiddle2, text="New", bg='light slate gray', width = 8, command= lambda: cleanUp(cleanUp_vars))
newBtn.grid(column=0, row=2, padx=(30,20), pady=5)

createBtn = Button(lowerMiddle2, text="Load", bg='light slate gray', width = 8, command= lambda: first_run(unit.get(), unit_shipment_date.get(), barcode.get(), gui_vars))
createBtn.grid(column=1, row=2, padx=20, pady=5)

transferBtn = Button(lowerMiddle2, text="Transfer", bg='light slate gray', width = 8, command= lambda: transferContent(unit.get(), unit_shipment_date.get(), barcode.get(), transfer_vars))
transferBtn.grid(column=2, row=2, padx=20, pady=5)

analyzeBtn = Button(lowerMiddle2, text="Analyze", bg='light slate gray', width = 8, command= lambda: analyzeContent(unit.get(), unit_shipment_date.get(), barcode.get(), analysis_vars))
analyzeBtn.grid(column=3, row=2, padx=20, pady=5)
    
closeBtn = Button(lowerMiddle2, text="Quit", bg='light slate gray', width = 8, command= lambda: closeUp(window))
closeBtn.grid(column=4, row=2, padx=20, pady=5)

mediaStatus = BooleanVar()
mediaStatus.set(False)
mediaStatusChk = Checkbutton(lowerMiddle2, text="Attached?", variable=mediaStatus)
mediaStatusChk.grid(column=5, row=2, padx=(10, 20), pady=5)

'''

GUI section for BDPL technician note

'''
noteFrame = Frame(window, width=650, height=40)
noteFrame.pack(fill=BOTH)

noteLabel = Label(noteFrame, text="BDPL\nnote:", anchor='w')
noteLabel.grid(row=1, column=0, pady=10)

noteScroll = Scrollbar(noteFrame)
noteField = Text(noteFrame, height=3)
noteScroll.config(command=noteField.yview)
noteField.config(yscrollcommand=noteScroll.set)

noteField.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=10)
noteFrame.grid_rowconfigure(1, weight=1)
noteFrame.grid_columnconfigure(1, weight=1)

noteScroll.grid(row=1, column=2, padx=(0, 10), pady=(10, 0), sticky=NS)

noteSave = Button(noteFrame, text="Save\nnote", width=5, command= lambda: writeNote(unit.get(), unit_shipment_date.get(), barcode.get(), gui_vars))
noteSave.grid(row=1, column=3, padx=10)

noteFail = BooleanVar()
noteFail.set(False)
noteFailChk = Checkbutton(noteFrame, text="Record failed transfer with note", variable=noteFail)
noteFailChk.grid(row=2, column=1, pady=(0, 10))

'''
GUI section for additional actions/features
'''
bottomFrame = Frame(window, width=650, height=50)
bottomFrame.pack(fill=BOTH)
bottomFrame.pack_propagate(False)

check_spreadsheet = Button(bottomFrame, text="Check spreadsheet", width = 20, command= lambda: check_progress(unit.get(), unit_shipment_date.get()))
check_spreadsheet.grid(row=0, column=0, padx=30)

move_pics = Button(bottomFrame, text="Move media images", width = 20, command= lambda: move_media_images(unit.get(), unit_shipment_date.get()))
move_pics.grid(row=0, column=1, padx=30)

unfinished_check = Button(bottomFrame, text="Check unfinished", width = 20, command= lambda: check_unfinished(unit.get(), unit_shipment_date.get()))
unfinished_check.grid(row=0, column=2, padx=30)

'''
GUI section with metadata      
'''

borderFrame = Frame(window, width=650, height=5, bg='black')
borderFrame.pack(fill=BOTH, padx=10, pady=10)
borderLabel = Label(borderFrame, text="Information about transfer:")
borderLabel.pack()
borderLabel.config(fg='white', bg='black')

inventoryFrame = Frame(window, width=650, height=300)
inventoryFrame.pack(fill=BOTH)

inventoryTop = Frame(inventoryFrame, width=650, height=50)
inventoryTop.pack(fill=BOTH)
#inventoryTop.pack_propagate(0)
inventoryTop.grid_columnconfigure(1, weight=1)

inventoryBottom = Frame(inventoryFrame, width=650, height=250)
inventoryBottom.pack(fill=BOTH)
#inventoryBottom.pack_propagate(0)
#inventoryBottom.grid_columnconfigure(0, weight=1)

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

window.mainloop()