import subprocess
import os
import re
import sys

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
    mmls_cmd = 'mmls {} > {}'.format(imagefile, mmls_out) 
    mmls_exit = subprocess.call(mmls_cmd, shell=True)


    disktype_out = os.path.join(folder, 'disktype.txt')
    dt_cmd = 'disktype {} > {}'.format(imagefile, disktype_out)
    subprocess.call(dt_cmd, shell=True)

    #first, check if mmls produced anything
    if mmls_exit != 0:
        print('Nothing reported by mmls')

    #first, get a list of all filesystems on disk
        fs_list = []
        with open(disktype_out, 'r') as f:
            for line in f:
                if 'file system' in line:
                        fs_list.append(line.lstrip().split(' file system', 1)[0])
            
        #now see if our list of file systems include either HFS, UDF, or ISO9660        
        check_list = ['UDF', 'ISO9660']
        if not any(fs in ' '.join(fs_list) for fs in check_list):
            print('FOUND UDF or ISO9660--CALL TERACOPY!')
            secureCopy()

        elif 'HFS' in ' '.join(fs_list):
            print('FOUND HFS!!! Call unhfs')
            unhfs_func('', '', imagefile)
        
        else:
            print('OTHER KIND OF FILE SYSYTEM! Call tsk_recover!')
            tsk_recover_func('', '', imagefile)

    #if we do have an mmls report, then pull our key data points out: slot, start, and description.  Create a dictionary for each partition and then save these to a list
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
    for part in partition_info:
        
        if 'osx' in part['desc']:
            
            out = os.path.join(folder, 'unhfs', "%s" % part['part_id'])
            if not os.path.exists(out):
                os.makedirs(out)
            unhfs_func(part['part_id'], out, imagefile)
        elif 'HFS' in part['desc']:
            
            out = os.path.join(folder, 'unhfs', "%s" % part['part_id'])
            if not os.path.exists(out):
                os.makedirs(out)
            unhfs_func(part['part_id'], out, imagefile)
        elif 'Apple' in part['desc']:
            
            out = os.path.join(folder, 'unhfs', "%s" % part['part_id'])
            if not os.path.exists(out):
                os.makedirs(out)
            unhfs_func(part['part_id'], out, imagefile)
        else:
            out = os.path.join(folder, 'tsk', "%s" % part['part_id'])
            if not os.path.exists(out):
                os.makedirs(out)
            tsk_recover_func(part['start'], out, imagefile)
            
        print(part)

if __name__ == '__main__':
    main()

