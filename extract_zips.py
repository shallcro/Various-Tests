import os
import zipfile
import shelve
import datetime
import csv

ship_dir = 'Z:/UAC/ingest/20210309'
item_info = 'Z:/UAC/ingest/20210309/item_ingest_info'
# out = 'C:/temp/bdpl_zip.txt'
# o_f = open(out, 'a')
# for d in os.listdir(item_info):
    # target = os.path.join(item_info, d, 'files')
    # if os.path.exists(target):
        # for root, dirs, files in os.walk(target):
            # for f in files:
                # z_ip = os.path.join(root, f).replace(os.sep, os.altsep)
                # if os.path.splitext(z_ip)[1].lower() == '.zip':
                    # o_f.write('{}\n'.format(z_ip))
# o_f.close()

existing = []
barcode_list = []
error_list = []

with open('C:/temp/bdpl_zip.txt', 'r') as f:
    for file in f.read().splitlines():
        print('\nWorking on:', file)
                
        barcode = file.split('/')[4]
        dir_name = os.path.splitext(file)[0]
            
        if os.path.exists(dir_name):
            print('\tAlready exists!'.format(dir_name))
            existing.append(file)
            continue
        else:
            print('\Making folders')
            os.makedirs(dir_name)
            
        
        #check zip file and then extract
        with zipfile.ZipFile(file, 'r') as zip_ref:
            print('\tTesting zip...')
            chk = zip_ref.testzip()
            if chk is None:
                print('\tExtracting zip...')
                zip_ref.extractall(dir_name)
            else:
                print('\tERROR!!!')
                error_list.append(file)
                continue
            
        #delete zip file
        print('\tDeleting zip...')
        os.remove(file)
        
        #record in log file
        print('\tWriting to log file...')
        timestamp =str(datetime.datetime.now())
        unpack_log = os.path.join(ship_dir, barcode, 'metadata', 'logs', 'unpack_log.csv')
        header = ['Archive File', 'Folder' 'Time']
        info = [file, dir_name, timestamp]
        
        if not os.path.exists(unpack_log):
            need_header = True
        else:
            need_header = False
            
        with open(unpack_log, 'a', encoding='utf8') as o_f:
            writer = csv.writer(o_f, lineterminator='\n')
            if need_header:
                writer.writerow(header)
            writer.writerow(info)
            
        #add premis metadata
        if barcode in barcode_list:
            continue
        else:
            print('\tWriting PREMIS...')
            my_shelve = os.path.join(item_info, '{}-info'.format(barcode))
            
            db = shelve.open(my_shelve, writeback=True)
            
            temp_dict = {}
            temp_dict['eventType'] = 'unpacking'
            temp_dict['eventOutcomeDetail'] = 0
            temp_dict['timestamp'] = str(datetime.datetime.now())
            temp_dict['eventDetailInfo'] = "with zipfile.ZipFile({}, 'r') as zip_ref: zip_ref.extractall({})".format(file, dir_name)
            temp_dict['eventDetailInfo_additional'] = "The process of extracting objects from .zip packages."
            temp_dict['linkingAgentIDvalue'] = 'python 3.7.3 zipfile.ZipFile.extractall()'
            
            db['premis'].append(temp_dict)
            db.sync()
            db.close()
            
            barcode_list.append(barcode)
            
    if len(existing) > 0:
        print('\n\nThese folders already existed and may have same content as .ZIP:\n\t{}'.format('\n\t'.join(existing)))
    
    if len(error_list) > 0:
        print('\n\nThese .ZIP files had errors:\n\t{}'.format('\n\t'.join(error_list)))
        
    print('\n\nRe-run analysis on these items:\n\t{}'.format('\n\t'.join(barcode_list)))
    
        