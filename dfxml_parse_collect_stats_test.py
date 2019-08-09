'''script to test parsing dfxml and then writing values to a dictionary'''

import os
import hashlib
import datetime
from lxml import etree as ET
import pickle

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    file_stats = []
    
    dfxml_output = os.path.join('C:/temp', 'dfxml-test.xml')

    for root, dirnames, filenames in os.walk('C:\\temp\\test2'):
        for file in filenames:
            
            target = os.path.join(root, file)
            
            size = os.path.getsize(target)
            
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(target)).isoformat()[:-7]
            
            ctime = datetime.datetime.fromtimestamp(os.path.getctime(target)).isoformat()[:-7]
            
            atime = datetime.datetime.fromtimestamp(os.path.getatime(target)).isoformat()[:-7]
            
            checksum = md5(target)
            
            file_dict = { 'name' : target, 'size' : size, 'mtime' : mtime, 'ctime' : ctime, 'atime' : atime, 'checksum' : checksum}
            
            file_stats.append(file_dict)
    
    for f in file_stats:
        print('name: {}\nsize: {}\nchecksum: {}\nlast modified: {}\ncreated: {}\naccessed: {}\n\n\n'.format(f['name'], str(f['size']), f['checksum'], f['mtime'], f['ctime'], f['atime']))
        
        
   
    print('\n\nGenerating DFXML from disk image metadata...')
    
    attr_qname = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    dfxml_namespace = 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML'
    dfxml_ns = "{%s}" % dfxml_namespace
    dc_namespace = 'http://purl.org/dc/elements/1.1/'
    dc = "{%s}" % dc_namespace
    NSMAP = {None : 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML',
            'xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'dc' : dc_namespace}

    dfxml = ET.Element("dfxml", nsmap=NSMAP, version="1.0")
    
    metadata = ET.SubElement(dfxml, "metadata")
    
    dctype = ET.SubElement(metadata, dc + "type")
    dctype.text = "Hash List"
    
    creator = ET.SubElement(dfxml, 'creator')
    
    program = ET.SubElement(creator, 'program')
    program.text = 'bdpl_ingest'
    
    execution_environment = ET.SubElement(creator, 'execution_environment')
    
    start_time = ET.SubElement(execution_environment, 'start_time')
    start_time.text = str(datetime.datetime.now().isoformat())
    
    for f in file_stats:
        fileobject = ET.SubElement(dfxml, 'fileobject')
        
        filename = ET.SubElement(fileobject, 'filename')
        filename.text = f['name']
        
        filesize = ET.SubElement(fileobject, 'filesize')
        filesize.text = str(f['size'])

        modifiedtime = ET.SubElement(fileobject, 'mtime')
        modifiedtime.text = f['mtime']
    
        createdtime = ET.SubElement(fileobject, 'ctime')
        createdtime.text = f['ctime']
        
        accesstime = ET.SubElement(fileobject, 'atime')
        accesstime.text = f['atime']
            
        hashdigest = ET.SubElement(fileobject, 'hashdigest', type='md5')
        hashdigest.text = f['checksum']

    tree = ET.ElementTree(dfxml)
        
    tree.write(dfxml_output, pretty_print=True, xml_declaration=True, encoding="utf-8")      
    
    with open ('Downloads\\pickle.txt', 'wb') as f:
        pickle.dump(file_stats, f)


if __name__ == '__main__':
    main()
