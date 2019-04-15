import subprocess
import os
import re
import sys
import Objects
import datetime
import math
import time

def time_to_int(str_time):
    """ Convert datetime to unix integer value """
    dt = time.mktime(datetime.datetime.strptime(str_time, 
        "%Y-%m-%dT%H:%M:%S").timetuple())
    return dt

def fix_dates(files_dir, dfxml_output):
    #adapted from Timothy Walsh's Disk Image Processor: https://github.com/CCA-Public/diskimageprocessor
    timestamp = str(datetime.datetime.now())
    
    print('\n\nFILE MAC TIME CORRECTION (USING DFXML)')
    
    try:
        for (event, obj) in Objects.iterparse(dfxml_output):
            # only work on FileObjects
            if not isinstance(obj, Objects.FileObject): -
                continue

            # skip directories and links
            if obj.name_type:
                if obj.name_type not in ["r", "d"]:
                    continue

            # record filename
            dfxml_filename = obj.filename
            dfxml_filedate = int(time.time()) # default to current time
            
            dfxml_partition = obj.partition
            
            print('filename :', dfxml_filename)
            print('partition: ', dfxml_partition)
            
            #continue

            # record last modified or last created date
            try:
                mtime = obj.mtime
                mtime = str(mtime)
            except:
                pass

            try:
                crtime = obj.crtime
                crtime = str(crtime)
            except:
                pass

            # fallback to created date if last modified doesn't exist
            if mtime and (mtime != 'None'):
                mtime = time_to_int(mtime[:19])
                dfxml_filedate = mtime
            elif crtime and (crtime != 'None'):
                crtime = time_to_int(crtime[:19])
                dfxml_filedate = crtime
            else:
                continue

            # rewrite last modified date of corresponding file in objects/files
            exported_filepath = os.path.join(files_dir, dfxml_filename)
            if os.path.isdir(exported_filepath):
                os.utime(exported_filepath, (dfxml_filedate, dfxml_filedate))
            elif os.path.isfile(exported_filepath):
                os.utime(exported_filepath, (dfxml_filedate, dfxml_filedate)) 
            else:
                continue

    except ValueError:
       pass

def disktype_info(disktype_out):
    with open(disktype_out, 'r') as f:
        for line in f:
            if 'file system' in line:
                    fs_list.append(line.lstrip().split(' file system', 1)[0])
    return fs_list

def secureCopy():
    copycmd = 'TERACOPY COPY F:\\ "C:\\temp\\mmls\\copy" /SkipAll /CLOSE'
    subprocess.call(copycmd, shell=True)

def tsk_recover_func(start, out, imagefile):
    if start == '':
        cmd = 'tsk_recover -a {} "C:\\temp\\mmls\\tsk'.format(imagefile) 
    else:
        cmd = 'tsk_recover -a -o {} {} {}'.format(start, imagefile, out)

    subprocess.call(cmd, shell=True)

def unhfs_func(start, out, imagefile):
    if start == '':
        cmd = 'unhfs -o "C:\\temp\\mmls\\unhfs" {}'.format(imagefile)
    else:
        cmd = 'unhfs -partition {} -o {} {}'.format(start, out, imagefile)
    
    subprocess.call(cmd, shell=True)

def main():

    imagefile = sys.argv[1]

    folder = 'C:\\temp\\mmls'

    mmls_out = os.path.join(folder, 'mmls.txt')
    mmls_cmd = 'mmls {} > {} 2> NUL'.format(imagefile, mmls_out) 
    mmls_exit = subprocess.call(mmls_cmd, shell=True)


    disktype_out = os.path.join(folder, 'disktype.txt')
    dt_cmd = 'disktype {} > {}'.format(imagefile, disktype_out)
    subprocess.call(dt_cmd, shell=True)

    #first, check if mmls produced anything
    if os.stat(mmls_out).st_size == 0:
        print('Nothing reported by mmls')

    #first, get a list of all filesystems on disk
        fs_list = []
        with open(disktype_out, 'r') as f:
            for line in f:
                if 'file system' in line:
                    fs_list.append(line.lstrip().split(' file system', 1)[0])
        
        if len(fs_list) > 0:
            print('found file systems: ', ', '.join(fs_list))
            
            #now see if our list of file systems include either HFS, UDF, or ISO9660        
            check_list = ['UDF', 'ISO9660']
            if any(fs in ' '.join(fs_list) for fs in check_list):
                print('FOUND UDF or ISO9660--CALL TERACOPY!')
                secureCopy()

            elif 'HFS' in ' '.join(fs_list):
                print('FOUND HFS!!! Call unhfs')
                unhfs_func('', '', imagefile)
            
            else:
                print('OTHER KIND OF FILE SYSYTEM! Call tsk_recover!')
                tsk_recover_func('', '', imagefile)
                
        else:
            print('disktype unable to ID file system(s)')
            
    #if we do have an mmls report, then pull our key data points out: slot, start, and description.  Create a dictionary for each partition and then save these to a list
    else:
        print('mmls found partitions')
        partition_info = []
        part_no = 0
        with open(mmls_out, 'r') as f:
            
            #skip the first 4 mmls header lines
            for line in f.readlines()[5:]:
                temp = {}
                #only read those lines that have numerical 'slot' info
                if any(s.isdigit() for s in re.split(r'\s\s+', line.rstrip())[1]):
                    temp['part_id'] = str(part_no).zfill(2)
                    temp['start'] = re.split(r'\s\s+', line.rstrip())[2]
                    temp['desc'] = re.split(r'\s\s+', line.rstrip())[5]
                    part_no += 1
                    #now save this dictionary to our list of partition info
                    partition_info.append(temp)
        #now go through the list to identify which need to be handled by unhfs and which by tsk_recover
        #list of potential descriptions to ID when unhfs is required
        unhfs_list = ['osx', 'hfs', 'Apple']
        
        for part in partition_info:
            
            if any(fs in part['desc'] for fs in unhfs_list):
                print('Found a Mac partition--using UNHFS')
                out = os.path.join(folder, 'unhfs', "%s" % part['part_id'])
                if not os.path.exists(out):
                    os.makedirs(out)
                unhfs_func(part['part_id'], out, imagefile)
            
            else:
                print('Other partition: using tsk_recover')
                out = os.path.join(folder, 'tsk', "partition-%s" % (int(part['part_id']) + 1))
                if not os.path.exists(out):
                    os.makedirs(out)
                tsk_recover_func(part['start'], out, imagefile)
                
                fix_dates(out, "C:\\temp\\mmls\\fiwalk.xml")
                
            print(part)

        
if __name__ == '__main__':
    main()

