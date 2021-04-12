import os
import shutil
import zlib
import datetime
import csv
import zipfile
import shelve

def crc32(fileName):
    with open(fileName, 'rb') as fh:
        hash = 0
        while True:
            s = fh.read(65536)
            if not s:
                break
            hash = zlib.crc32(s, hash)
        return "%08X" % (hash & 0xFFFFFFFF)

def check_path(file_path):
    if not os.path.exists(file_path):
        print(os.path.basename(file_path), 'does not exist')
        return False
    else:
        return True

def main():

    global barcode, ship_dir, scan_dir, list_of_files, log_file, dest, cut_path, zip_file_list, item_info
    
    barcode = input('Enter barcode: ')
    ship_dir = input('Enter path to shipment directory: ')
    scan_dir = input('Enter path to target directory: ')
    
    list_of_files = os.path.join('Z:/bdpl_transfer_lists', '{}.txt'.format(barcode))
    
    log_file = os.path.join(ship_dir, barcode, 'metadata', 'logs', 'copy_log.csv')   
    dest = os.path.join(ship_dir, barcode, 'files')
    
    zip_file_list = 'C:/temp/bdpl_zip.txt'
    
    item_info = os.path.join(ship_dir, 'item_ingest_info')    
    
    for dir in (ship_dir, scan_dir, dest):
        status = check_path(dir)
        if not status:
            return
        
    cut_path = input('Trim source path at this point: ')
    
    file_list()
    copy_files()
    extract_zips()
    

def file_list():

    avoid_ext = []

    include_ext = []

    avoid_files = []

    avoid_dirs = []
    
    zfl = open(zip_file_list, 'w')

    with open(list_of_files, 'w', encoding='utf8') as f:

        for root, dirs, files in os.walk(scan_dir):
            for file in files:
            
                file_ext = os.path.splitext(file)[1].lower()
                
                if file.lower() in  ['thumbs.db', '.ds_store']:
                    continue
                
                if len(include_ext) > 0:
                    if not file_ext in include_ext:
                        continue
                
                if len(avoid_ext) > 0:
                    if file_ext in avoid_ext:
                        continue
                
                target = os.path.join(root, file).replace(os.sep, os.altsep)
                
                if len(avoid_files) > 0:
                    if target in avoid_files:
                        continue
                    
                if len(avoid_dirs) > 0:
                    if any(i in os.path.dirname(target) for i in avoid_dirs):
                        continue
                        
                if file_ext == '.zip':
                    zfl.write('{}\n'.format(target))
                    
                f.write('{}\n'.format(target))
        
    zfl.close()
    
    print('\nFile list is compiled!')

def copy_files():
    
    header = ['File', 'Source CRC', 'Destination CRC', 'Time']
    
    copy_error = False

    with open(log_file, 'w', encoding='utf8') as o_f:
        writer = csv.writer(o_f, lineterminator='\n')
        writer.writerow(header)        
        
        print('Reviewing list....\n\n')
        
        with open(list_of_files, 'r', encoding='utf8') as i_f:
            counter = 0
            temp_list = i_f.read().splitlines()
            total = len(temp_list)
            
            for file in temp_list:
            
                counter += 1
                
                print('Working on file {} of {}'.format(counter, total))
                
                crc_source = crc32(file)
                
                rel_path = os.path.relpath(os.path.dirname(file), cut_path)
                
                dest_path = os.path.join(dest, rel_path)
                
                moved_file = os.path.join(dest_path, os.path.basename(file))
                
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                    
                shutil.copy(file, dest_path)
                
                if os.path.exists(moved_file):
                    crc_dest = crc32(moved_file)
                else:
                    print('Error:', file)
                    copy_error = True
                    continue
                
                if crc_source != crc_dest:
                    dest_file = os.path.join(dest_path, os.path.basename(file))
                    try:
                        os.remove(dest_file)
                    except:
                        pass
                        
                    copy_error = True
                
                timestamp = str(datetime.datetime.now())
                
                info = [moved_file, crc_source, crc_dest, timestamp]
                writer.writerow(info)
                
    if copy_error:
        print('\nCheck errors and manually copy files as needed')
    else:
        print('\nCopy complete!')       
        
    temp_dict = {}
    temp_dict['eventType'] = 'replication'
    temp_dict['eventOutcomeDetail'] = 0
    temp_dict['timestamp'] = timestamp
    temp_dict['eventDetailInfo'] = "python copy.shutil with CRC32 hash comparison".format(file, dir_name)
    temp_dict['eventDetailInfo_additional'] = "The process of creating a copy of an object that is, bit-wise, identical to the original."
    temp_dict['linkingAgentIDvalue'] = 'python 3.7.3'
    
    write_premis(temp_dict)

def write_premis(temp_dict):
    my_shelve = os.path.join(item_info, '{}-info'.format(barcode))
    
    db = shelve.open(my_shelve, writeback=True)
    
    db['premis'].append(temp_dict)
    db.sync()
    db.close()
        
def extract_zips():

    existing = []
    barcode_list = []
    error_list = []

    with open(zip_file_list, 'r') as f:
        f_ls = f.read().splitlines()
        total = len(f_ls)
        if total == 0:
            return
            
        counter = 0
        for file in f.read().splitlines():
            counter +=1
            
            print('\nWorking on .zip {} of {} ({})'.format(counter, total, file))
                    
            barcode = file.split('/')[4]
            dir_name = os.path.splitext(file)[0]
                
            if os.path.exists(dir_name):
                print('\tAlready exists!'.format(dir_name))
                existing.append(file)
                continue
            else:
                print('\tMaking folders')
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
                temp_dict = {}
                temp_dict['eventType'] = 'unpacking'
                temp_dict['eventOutcomeDetail'] = 0
                temp_dict['timestamp'] = timestamp
                temp_dict['eventDetailInfo'] = "with zipfile.ZipFile(file, 'r') as zip_ref: zip_ref.extractall(dir_name)"
                temp_dict['eventDetailInfo_additional'] = "The process of extracting objects from .zip packages."
                temp_dict['linkingAgentIDvalue'] = 'python 3.7.3 zipfile.ZipFile.extractall()'
                
                write_premis(temp_dict)
                
                barcode_list.append(barcode)
                
    if len(existing) > 0:
        print('\n\nThese folders already existed and may have same content as .ZIP:\n\t{}'.format('\n\t'.join(existing)))
    
        if len(error_list) > 0:
            print('\n\nThese .ZIP files had errors:\n\t{}'.format('\n\t'.join(error_list)))
            
        print('\n\nRe-run analysis on these items:\n\t{}'.format('\n\t'.join(barcode_list)))
                   
if __name__ == '__main__':
    main()