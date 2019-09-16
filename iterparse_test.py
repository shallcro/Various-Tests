from lxml import etree
import pickle

dfxml_output = 'Z:/TEST/files/30000152020792-dfxml.xml'
temp_dir = 'Z:/UAC/ingest/20190819/30000152020792/temp'

file_stats = []

counter = 0

for event, element in etree.iterparse(dfxml_output, events = ("end",), tag="fileobject"):
    counter =+ 1
    print('\nWorking on item ', counter)
    file_dict = {}
    
    
    good = True
    mt = False
    mtime = 'undated'
    
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
        if child.tag == "filesize":
            size = child.text
        if child.tag == "hashdigest":
            checksum = child.text
        if child.tag == "mtime":
            mtime = child.text
            mt = True
        if child.tag == "crtime" and mt == False:
            mtime = child.text

    if good:
        file_dict = { 'name' : target, 'size' : size, 'mtime' : mtime, 'checksum' : checksum}
        file_stats.append(file_dict)
    
    element.clear()
    
checksums = os.path.join(temp_dir, 'checksums.txt')
with open (checksums, 'wb') as f:
    pickle.dump(file_stats, f)
