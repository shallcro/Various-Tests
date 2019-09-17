from lxml import etree
import pickle
import datetime
import os

dfxml_output = input('Path to dfxml: ')
temp_dir = input('Path to temp folder: ')

file_stats = []

counter = 0

for event, element in etree.iterparse(dfxml_output, events = ("end",), tag="fileobject"):
    counter += 1
    print('\nWorking on item ', counter)
    file_dict = {}
    
    
    good = True
    mt = False
    mtime = 'undated'
    
    for child in element:
        
        if child.tag == "filename":
            target = child.text
            print('\rCollecting stats for: %s' % target, end='')
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
        if child.tag == "filesize":
            size = child.text
        if child.tag == "hashdigest":
            checksum = child.text
        if child.tag == "mtime":
            mtime = datetime.datetime.utcfromtimestamp(int(child.text)).isoformat()
            mt = True
        if child.tag == "crtime" and mt == False:
            mtime = datetime.datetime.utcfromtimestamp(int(child.text)).isoformat()

    if good:
        file_dict = { 'name' : target, 'size' : size, 'mtime' : mtime, 'checksum' : checksum}
        file_stats.append(file_dict)
    
    element.clear()
    
checksums = os.path.join(temp_dir, 'checksums.txt')
with open (checksums, 'wb') as f:
    pickle.dump(file_stats, f)
