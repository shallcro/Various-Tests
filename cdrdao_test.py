'''
Script to test content and metadata extraction with cdrdao
'''

import subprocess
import os
import random
import string

barcode = ''.join(random.choice(string.digits) for x in range(7))

if not os.path.exists('C:\\temp\\cdda'):
    os.makedirs('C:\\temp\\cdda')

#determine appropriate drive ID for cdrdao; save output of command to log file
cdr_scan_log = 'C:\\temp\\cdda\\scan.log'
scan_cmd = 'cdrdao scanbus > %s 2>&1' % cdr_scan_log
subprocess.check_output(scan_cmd, shell=True)

#pull drive ID from file
with open(cdr_scan_log, 'rb') as f:
    drive_id = f.read().splitlines()[8].split(':')[0]

#get info about CD; record this as a premis event, too.
disk_info_log = 'C:\\temp\\cdda\\cdr_info.log'
cmd = 'cdrdao disk-info --device %s --driver generic-mmc-raw > %s 2>&1' % (drive_id, disk_info_log)

exitcode = subprocess.call(cmd, shell=True)

#read log file to determine # of sessions on disk.
with open(disk_info_log, 'rb') as f:
    sessions = int(f.read().splitlines()[21].split(':')[1].strip())

#for each session, create a bin/toc file
for x in range(1, (sessions+1)):
    cdr_bin = os.path.join("C:\\temp\\cdda", "%s-%s.bin") % (barcode, str(sessions).zfill(2))
    cdr_toc = os.path.join("C:\\temp\\cdda", "%s-%s.toc") % (barcode, str(sessions).zfill(2))
    
    cdr_cmd = 'cdrdao read-cd --read-raw --datafile %s --device %s --driver generic-mmc-raw %s' % (drive_id, cdr_bin, cdr_toc)
    
    exitcode = subprocess.call(cdr_cmd, shell=True)
    
    #need to write PREMIS
    
    #convert TOC to CUE
    cue = os.path.join("C:\\temp\\cdda", "%s-%s.cue") % (barcode, str(sessions).zfill(2))
    t2c_cmd = 'toc2cue %s %s' % (cdr_toc, cue)
    
    subprocess.check_output(t2c_cmd, shell=True)

#now rip to WAV using cdparanoia
paranoia_log = os.path.join('C:\\temp\\cdda', '%s-cdparanoia.log' % barcode)
paranoia_out = os.path.join('C:\\temp\\cdda', '%s.wav' % barcode)

paranoia_cmd = 'cd-paranoia -l %s -w [00:00:00.00]- %s' % (paranoia_log, paranoia_out)

exitcode = subprocess.call(paranoia_cmd, shell=True)
