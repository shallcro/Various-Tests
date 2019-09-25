import csv
import os

infile = input('Enter path to csv: ')

report_dir = os.path.dirname(infile)

unidentified = os.path.join(report_dir, 'unidentified.csv')

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
            
            filename = row[2].split('file:/', 1)[1]
            filesize = row[7]
            modified = row[10]
            errors = ''
            namespace = 'pronom'
            if row[14] == "":
                id = 'UNKNOWN'
            else:
                id = row[14]
            format = row[16]
            version = row[17]
            mime = row[15]
            basis = ''
            if row[11].lower() == 'true':
                warning = 'extension mismatch'
            else:
                warning = ''
            
            
            data = [filename, filesize, modified, errors, namespace, id, format, version, mime, basis, warning]
            csvWriter.writerow(data)
            
            if id == 'UNKNOWN':
                with open(unidentified, 'a', newline='') as f3:
                    csvWriter2 = csv.writer(f3)
                    csvWriter2.writerow(data)