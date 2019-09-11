'''
Script to correct file timestamp.  Spreadsheet must be have no headers and include full path to file in first column and desired file timestamp in second, in format YYYY-MM-DD HH:MM:SS
'''

import datetime
import openpyxl
import os
import time

book = input('Enter Python-appropriate path to spreadsheet: ')

wb = openpyxl.load_workbook(book)

ws = wb['Sheet1']

iterrows = ws.iter_rows()

for row in iterrows:
    target = row[0].value
    
    date = datetime.datetime.strptime(str(row[1].value), '%Y-%m-%d %H:%M:%S')
    
    modtime = time.mktime(date.timetuple())
    
    print('File: %s\tTime: %s' % (target, modtime))
    os.utime(target, (modtime, modtime))
