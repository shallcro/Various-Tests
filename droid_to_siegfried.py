import csv
import os

infile = input('Enter path to csv: ')

report_dir = os.path.dirname(infile)

outfile = os.path.join(report_dir, 'siegfried.csv')
counter = 0
with open(outfile, 'w', newline='') as f1:
    csvWriter = csv.writer(f1)
    header = ['filename', 'filesize', 'modified', 'errors', 'namespace', 'id', 'format', 'version', 'mime', 'basis', 'warning']
    csvWriter.writerow(header)
    with open(infile, 'r', encoding='utf8') as f2:
        csvReader = csv.reader(f2)
        next(csvReader)
        for row in csvReader:
            counter+=1
            print('\rWorking on row %d' % counter, end='')
            if row[11] == 'TRUE':
                warning = 'extension mismatch'
            else:
                warning = ''
            data = [row[2].split('file:/', 1)[1], row[7], row[10], '', 'pronom', row[14], row[16], row[15], '', '']
            csvWriter.writerow(data)