<<<<<<< HEAD
#This was taken from bdpl_ingest.py; probably needs some additional work to actually run...

def main():
    if not tsk_loaddb(tsk_db, bdpl_vars()['imagefile'])
        print '\n\nDisk image metadata extraction failed with the following error:\n\n%s' % message                   
    else:
        #connect to database created by tsk_loaddb.
        tsk_conn=sqlite3.connect(tsk_db)
        c=tsk_conn.cursor()
        
        #get the names of all relevant tables; then close database
        for tablename in c.execute("SELECT name FROM sqlite_master WHERE type='table' and name NOT LIKE 'sqlite_%';"):
            tableloop(tablename[0], tsk_db)
        c.close()
        tsk_conn.close()
            
        #parse disk image metadata; create a dictionary of data points
        dfxml_from_image(tsk_db, dfxml_output)

def tsk_loaddb(tsk_db, imagefile):
    print 'Running tsk_loaddb: collecting metadata from disk image'
    #create sqlite db from image
    tsk_loaddb_command = 'tsk_loaddb -h -d %s %s' % (tsk_db, imagefile)
    
    pipes = subprocess.Popen(tsk_loaddb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    pipes.wait()
    std_out, std_err = pipes.communicate()
    if "Error" in std_err or pipes.returncode != 0:
        print '\n\nDisk image metadata extraction failed with the following error:\n\n%s' % std_err
        return False
    else:
        return True

def tableloop(tablename, tsk_db): 
    sql_command = 'sqlite3 -header -csv %s "SELECT * from %s;"' % (tsk_db, tablename)
    csvfile = os.path.join(bdpl_vars()['temp_dir'], '%s.csv' % tablename)
    with open(csvfile, "wb") as output:
        subprocess.call(sql_command, stdout=output, shell=True)


def dfxml_from_image(tsk_db, dfxml_output):
    print '\n\nGathering information to produce DFXML...'
    
    #set variables
    temp_dir = bdpl_vars()['temp_dir']
    disktype_output = os.path.join(bdpl_vars()['reports_dir'], 'disktype.txt')
    dfxml_dict = {}
    file_list = []

    #pull info from csv files 
    tsk_fs_info = os.path.join(temp_dir, 'tsk_fs_info.csv')
    with open(tsk_fs_info) as csvfile:
        data_tsk_fs_info = [row for row in csv.reader(csvfile)]
    
    tsk_files = os.path.join(temp_dir, 'tsk_files.csv')
    with open(tsk_files) as csvfile:
        data_tsk_files = [row for row in csv.reader(csvfile)]
    
    tsk_image_info = os.path.join(temp_dir, 'tsk_image_info.csv')
    with open(tsk_image_info) as csvfile:
        data_tsk_image_info = [row for row in csv.reader(csvfile)]
    
    tsk_file_layout = os.path.join(temp_dir, 'tsk_file_layout.csv')
    with open(tsk_file_layout) as csvfile:
        data_tsk_file_layout = [row for row in csv.reader(csvfile)]
    
    tsk_objects = os.path.join(temp_dir, 'tsk_objects.csv')
    with open(tsk_objects) as csvfile:
        data_tsk_objects = [row for row in csv.reader(csvfile)]

    #add info for DFXML   
    dfxml_dict['creator_program'] = "IU Born-Digital Preservation Transfer and Ingest Process"
    dfxml_dict['type'] = 'Disk Image'
    #dfxml_dict['cmd_line'] = ' '.join(map(str, sys.argv))
    dfxml_dict['start_time'] = datetime.datetime.now().replace(microsecond=0).isoformat()
    dfxml_dict['vol_offset'] = data_tsk_fs_info[1][1]
    dfxml_dict['part_offset'] = data_tsk_fs_info[1][1]
    dfxml_dict['sect_size'] = data_tsk_image_info[1][2]
    dfxml_dict['blk_size'] = data_tsk_fs_info[1][3]
    dfxml_dict['ftype'] = data_tsk_fs_info[1][2]
    dfxml_dict['blk_ct'] = data_tsk_fs_info[1][4]
    
    #get human-readable file system info from disktype and fsstat
    if os.path.exists(disktype_output):
        with open(disktype_output, 'rb') as f:
            for line in f:
                if 'file system' in line:
                    dfxml_dict['ftype_str'] = ' '.join(line.split()[0:])
                    break
                else:
                    continue
    else:
        dfxml_dict['ftype_str'] = 'Not recorded'
    
    
    fsstat_output = os.path.join(bdpl_vars()['reports_dir'], 'fsstat.txt')
    #set default values--just in case...
    dfxml_dict['fst_blk'] = '0'
    dfxml_dict['lst_blk'] = data_tsk_fs_info[1][4]
    
    if os.path.exists(fsstat_output):
        with open(fsstat_output, 'rb') as f:
            for line in f:
                if 'Total Range:' in line:
                    dfxml_dict['fst_blk'] = line.split()[2]
                    dfxml_dict['lst_blk'] = line.split()[4]
                    break
                else:
                    continue
    
    #now get information on all the files; skip the header row (1) and root row (2)
    for file in data_tsk_files[2:]:
        #skip if object is slack space
        if file[8] == '7':
            continue
        else:    
            file_dict = {}
            file_dict['filename'] = "%s%s" % (file[25][1:], file[5])
            
            #get the parent object ID
            child = file[0]
            for obj in data_tsk_objects[1:]:
                if child == "%s" % obj[0]:
                    parent_id = obj[1]
            sql_command = 'sqlite3 %s "SELECT meta_addr from tsk_files WHERE obj_id = %s;"' % (tsk_db, parent_id)
            file_dict['parent_inode'] = subprocess.check_output(sql_command, shell=True).rstrip()
            
            #get Last file / metadata status change time
            if file[16] == '0' or file[16] == '':
                pass
            else:
                file_dict['ctime'] = datetime.datetime.utcfromtimestamp(float(file[16])).isoformat()
            
            #get created time
            if file[17] == '0' or file[17] == '':
                pass
            else:
                file_dict['crtime'] = datetime.datetime.utcfromtimestamp(float(file[17])).isoformat()
            
            #get last access time
            if file[18] == '0' or file[18] == '':
                pass
            else:
                file_dict['atime'] = datetime.datetime.utcfromtimestamp(float(file[18])).isoformat()
            
            #get last modified time
            if file[19] == '0' or file[19] == '':
                pass
            else:
                file_dict['mtime'] = datetime.datetime.utcfromtimestamp(float(file[19])).isoformat()
            
            file_dict['size'] = file[15]
            file_dict['part'] = file[2]
            file_dict['id'] = file[0]
            file_dict['meta_type'] = file[12]
            
            if file[12] == '4':
                file_dict['name_type'] = 'c'
            
            elif file[12] == '2':
                file_dict['name_type'] = 'd'
            
            elif file[12] == '3':
                file_dict['name_type'] = 'p'
            
            elif file[12] == '1':
                file_dict['name_type'] = 'r'
            
            elif file[12] == '6':
                file_dict['name_type'] = 'l'
            
            elif file[12] == '5':
                file_dict['name_type'] = 'b'
            
            elif file[12] == '8':
                file_dict['name_type'] = 'h'
            
            elif file[12] == '7':
                file_dict['name_type'] = 's'
            
            elif file[12] >= '10':
                file_dict['name_type'] = 'v'
            
            elif file[12] == '9':
                file_dict['name_type'] = 'w'
                
            else:
                file_dict['name_type'] = '-'
                
            if file[13] == '1':
                file_dict['alloc'] = file[13]
            else:
                file_dict['alloc'] = '0'
            file_dict['inode'] = file[6]
            file_dict['mode'] = file[20]
            file_dict['uid'] = file[21]
            file_dict['gid'] = file[22]
            file_dict['md5'] = file[23]
            
            #check to see if any metadata elements used; if so, 'used' is true; otherwise false
            for u in file_dict.values():
                if len(u) > 0:
                    file_dict['used'] = '1'
                    break
                else:
                    file_dict['used'] = '0'
            
            #figure out byte runs; get the obj_id for the files and associated slack space
            id_list = []
            
            if file[6] == '':
                id_list = [file[0]]
            else:
                sql_byte_cmd = 'sqlite3 %s -newline " " "SELECT obj_id from tsk_files WHERE meta_addr = %s;"' % (tsk_db, file[6])
                id_list = []
                id_list = subprocess.check_output(sql_byte_cmd, shell=True).split()
                
                                
                #get size (in bytes) of slack space so that we can accurately represent len of files in DFXML
                sql_slack_cmd = 'sqlite3 %s -newline " " "SELECT size from tsk_files WHERE meta_addr = %s and type = 7;"' % (tsk_db, file[6])
                
                slack_list = []
                slack_list = map(int, subprocess.check_output(sql_slack_cmd, shell=True).split())
                
                if len(slack_list) == 0:
                    slack_list = [0]
                        
            #now loop through tsk_file_layout (skipping header)
            bytestart_list = []
            bytelen_list = []
            
            for run in data_tsk_file_layout[1:]:
                #check to see if the obj_ids are in the first column of tsk_file_layout; if so, add byte start and byte len info to lists
                if id_list[0] == run[0] :
                    bytestart_list.append(int(run[1]))
                    bytelen_list.append(int(run[2]))
                if len(id_list) > 1:
                    if id_list[1] == run[0]:
                        bytestart_list.append(int(run[1]))
                        bytelen_list.append(int(run[2]))
                            
            if len(bytestart_list) > 0:
                file_dict['bytelen_list'] = bytelen_list
                file_dict['bytestart_list'] = bytestart_list
                file_dict['slack_list'] = slack_list
            
            #append current dictionary to master list of file info
            file_list.append(file_dict)


    print '\n\nGenerating DFXML from disk image metadata...'
    
    attr_qname = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    dfxml_namespace = 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML'
    dfxml_ns = "{%s}" % dfxml_namespace
    dc_namespace = 'http://purl.org/dc/elements/1.1/'
    dc = "{%s}" % dc_namespace
    NSMAP = {'dc' : dc_namespace, 
             'xsi': "http://www.w3.org/2001/XMLSchema-instance", 
             None : dfxml_namespace}

    dfxml = ET.Element("dfxml", version="1.0", nsmap=NSMAP)
    
    metadata = ET.SubElement(dfxml, "metadata")
    
    dctype = ET.SubElement(metadata, dc + "type")
    dctype.text = dfxml_dict['type']
    
    creator = ET.SubElement(dfxml, 'creator')
    
    program = ET.SubElement(creator, 'program')
    program.text = dfxml_dict['creator_program']
    
    execution_environment = ET.SubElement(creator, 'execution_environment')
    
    #command_line = ET.SubElement(execution_environment, 'command_line')
    #command_line.text = dfxml_dict['cmd_line']
    
    start_time = ET.SubElement(execution_environment, 'start_time')
    start_time.text = dfxml_dict['start_time']
    
    sourceDir = ET.SubElement(dfxml, 'source')
    
    image_filename = ET.SubElement(sourceDir, 'image_filename')
    image_filename.text = bdpl_vars()['imagefile']
    
    volume = ET.SubElement(dfxml, 'volume', offset='%s' % dfxml_dict['vol_offset'])
    
    partition_offset = ET.SubElement(volume, 'partition_offset')
    partition_offset.text = dfxml_dict['part_offset']
    
    sector_size = ET.SubElement(volume, 'sector_size')
    sector_size.text = dfxml_dict['sect_size']
    
    block_size = ET.SubElement(volume, 'block_size')
    block_size.text = dfxml_dict['blk_size']
    
    ftype = ET.SubElement(volume, 'ftype')
    ftype.text = dfxml_dict['ftype']
    
    ftype_str = ET.SubElement(volume, 'ftype_str')
    ftype_str.text = dfxml_dict['ftype_str']
    
    block_count = ET.SubElement(volume, 'block_count')
    block_count.text = dfxml_dict['blk_ct']
    
    first_block = ET.SubElement(volume, 'first_block')
    first_block.text = dfxml_dict['fst_blk']
    
    last_block = ET.SubElement(volume, 'last_block')
    last_block.text = dfxml_dict['lst_blk']
    
    for f in file_list:
        fileobject = ET.SubElement(volume, 'fileobject')
        parent_object = ET.SubElement(fileobject, 'parent_object')
        po_inode = ET.SubElement(parent_object, 'inode')
        po_inode.text = f['parent_inode']
        
        filename = ET.SubElement(fileobject, 'filename')
        filename.text = f['filename']
        
        partition = ET.SubElement(fileobject, 'partition')
        partition.text = f['part']
        
        fo_id = ET.SubElement(fileobject, 'id')
        fo_id.text = f['id']
        
        name_type = ET.SubElement(fileobject, 'name_type')
        name_type.text = f['name_type']
        
        filesize = ET.SubElement(fileobject, 'filesize')
        filesize.text = f['size']
        
        alloc = ET.SubElement(fileobject, 'alloc')
        alloc.text = f['alloc']
        
        inode = ET.SubElement(fileobject, 'inode')
        inode.text = f['inode']
        
        meta_type = ET.SubElement(fileobject, 'meta_type')
        meta_type.text = f['meta_type']
        
        mode = ET.SubElement(fileobject, 'mode')
        mode.text = f['mode']
        
        nlink = ET.SubElement(fileobject, 'nlink')
        
        uid = ET.SubElement(fileobject, 'uid')
        uid.text = f['uid']
        
        gid = ET.SubElement(fileobject, 'gid')
        gid.text = f['gid']
        
        if 'ctime' in f:
            mtime = ET.SubElement(fileobject, 'ctime')
            mtime.text = f['ctime']
        
        if 'crtime' in f:
            mtime = ET.SubElement(fileobject, 'crtime')
            mtime.text = f['crtime']
            
        if 'atime' in f:
            mtime = ET.SubElement(fileobject, 'atime')
            mtime.text = f['atime']
            
        if 'mtime' in f:
            mtime = ET.SubElement(fileobject, 'mtime')
            mtime.text = f['mtime']
        
        if 'bytestart_list' in f:
            byte_runs = ET.SubElement(fileobject, 'byte_runs')
            
            #use lists to calculate byte runs
            i = 0
                        
            for item in f['bytestart_list']:
                fs_os = str(f['bytestart_list'][i])
                img_os = str(f['bytestart_list'][i])
                
                #first byte run will have a file/fs offset of 0; all others will have byte_start as reported in tsk_file_layout 
                if i == 0:
                    file_os = '0'
                else:
                    file_os = str(sum(f['bytelen_list'][:i]))
                
                #final len will need to subtract size of slack space to accurately report file size
                if i == (len(f['bytestart_list']) - 1):
                    bytelen = str(f['bytelen_list'][i] - sum(f['slack_list']))
                else:
                    bytelen = str(f['bytelen_list'][i])
                
                byteattributes = {"file_offset":'%s' % file_os, "fs_offset":'%s' % fs_os, "img_offset":'%s' % img_os, "len":'%s' % bytelen}
                
                byte_run = ET.SubElement(byte_runs, 'byte_run', byteattributes)
            
                i += 1
            
        hashdigest = ET.SubElement(fileobject, 'hashdigest', type='md5')
        hashdigest.text = f['md5']

    tree = ET.ElementTree(dfxml)
        
=======
#This was taken from bdpl_ingest.py; probably needs some additional work to actually run...

def main():
    if not tsk_loaddb(tsk_db, bdpl_vars()['imagefile'])
        print '\n\nDisk image metadata extraction failed with the following error:\n\n%s' % message                   
    else:
        #connect to database created by tsk_loaddb.
        tsk_conn=sqlite3.connect(tsk_db)
        c=tsk_conn.cursor()
        
        #get the names of all relevant tables; then close database
        for tablename in c.execute("SELECT name FROM sqlite_master WHERE type='table' and name NOT LIKE 'sqlite_%';"):
            tableloop(tablename[0], tsk_db)
        c.close()
        tsk_conn.close()
            
        #parse disk image metadata; create a dictionary of data points
        dfxml_from_image(tsk_db, dfxml_output)

def tsk_loaddb(tsk_db, imagefile):
    print 'Running tsk_loaddb: collecting metadata from disk image'
    #create sqlite db from image
    tsk_loaddb_command = 'tsk_loaddb -h -d %s %s' % (tsk_db, imagefile)
    
    pipes = subprocess.Popen(tsk_loaddb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    pipes.wait()
    std_out, std_err = pipes.communicate()
    if "Error" in std_err or pipes.returncode != 0:
        print '\n\nDisk image metadata extraction failed with the following error:\n\n%s' % std_err
        return False
    else:
        return True

def tableloop(tablename, tsk_db): 
    sql_command = 'sqlite3 -header -csv %s "SELECT * from %s;"' % (tsk_db, tablename)
    csvfile = os.path.join(bdpl_vars()['temp_dir'], '%s.csv' % tablename)
    with open(csvfile, "wb") as output:
        subprocess.call(sql_command, stdout=output, shell=True)


def dfxml_from_image(tsk_db, dfxml_output):
    print '\n\nGathering information to produce DFXML...'
    
    #set variables
    temp_dir = bdpl_vars()['temp_dir']
    disktype_output = os.path.join(bdpl_vars()['reports_dir'], 'disktype.txt')
    dfxml_dict = {}
    file_list = []

    #pull info from csv files 
    tsk_fs_info = os.path.join(temp_dir, 'tsk_fs_info.csv')
    with open(tsk_fs_info) as csvfile:
        data_tsk_fs_info = [row for row in csv.reader(csvfile)]
    
    tsk_files = os.path.join(temp_dir, 'tsk_files.csv')
    with open(tsk_files) as csvfile:
        data_tsk_files = [row for row in csv.reader(csvfile)]
    
    tsk_image_info = os.path.join(temp_dir, 'tsk_image_info.csv')
    with open(tsk_image_info) as csvfile:
        data_tsk_image_info = [row for row in csv.reader(csvfile)]
    
    tsk_file_layout = os.path.join(temp_dir, 'tsk_file_layout.csv')
    with open(tsk_file_layout) as csvfile:
        data_tsk_file_layout = [row for row in csv.reader(csvfile)]
    
    tsk_objects = os.path.join(temp_dir, 'tsk_objects.csv')
    with open(tsk_objects) as csvfile:
        data_tsk_objects = [row for row in csv.reader(csvfile)]

    #add info for DFXML   
    dfxml_dict['creator_program'] = "IU Born-Digital Preservation Transfer and Ingest Process"
    dfxml_dict['type'] = 'Disk Image'
    #dfxml_dict['cmd_line'] = ' '.join(map(str, sys.argv))
    dfxml_dict['start_time'] = datetime.datetime.now().replace(microsecond=0).isoformat()
    dfxml_dict['vol_offset'] = data_tsk_fs_info[1][1]
    dfxml_dict['part_offset'] = data_tsk_fs_info[1][1]
    dfxml_dict['sect_size'] = data_tsk_image_info[1][2]
    dfxml_dict['blk_size'] = data_tsk_fs_info[1][3]
    dfxml_dict['ftype'] = data_tsk_fs_info[1][2]
    dfxml_dict['blk_ct'] = data_tsk_fs_info[1][4]
    
    #get human-readable file system info from disktype and fsstat
    if os.path.exists(disktype_output):
        with open(disktype_output, 'rb') as f:
            for line in f:
                if 'file system' in line:
                    dfxml_dict['ftype_str'] = ' '.join(line.split()[0:])
                    break
                else:
                    continue
    else:
        dfxml_dict['ftype_str'] = 'Not recorded'
    
    
    fsstat_output = os.path.join(bdpl_vars()['reports_dir'], 'fsstat.txt')
    #set default values--just in case...
    dfxml_dict['fst_blk'] = '0'
    dfxml_dict['lst_blk'] = data_tsk_fs_info[1][4]
    
    if os.path.exists(fsstat_output):
        with open(fsstat_output, 'rb') as f:
            for line in f:
                if 'Total Range:' in line:
                    dfxml_dict['fst_blk'] = line.split()[2]
                    dfxml_dict['lst_blk'] = line.split()[4]
                    break
                else:
                    continue
    
    #now get information on all the files; skip the header row (1) and root row (2)
    for file in data_tsk_files[2:]:
        #skip if object is slack space
        if file[8] == '7':
            continue
        else:    
            file_dict = {}
            file_dict['filename'] = "%s%s" % (file[25][1:], file[5])
            
            #get the parent object ID
            child = file[0]
            for obj in data_tsk_objects[1:]:
                if child == "%s" % obj[0]:
                    parent_id = obj[1]
            sql_command = 'sqlite3 %s "SELECT meta_addr from tsk_files WHERE obj_id = %s;"' % (tsk_db, parent_id)
            file_dict['parent_inode'] = subprocess.check_output(sql_command, shell=True).rstrip()
            
            #get Last file / metadata status change time
            if file[16] == '0' or file[16] == '':
                pass
            else:
                file_dict['ctime'] = datetime.datetime.utcfromtimestamp(float(file[16])).isoformat()
            
            #get created time
            if file[17] == '0' or file[17] == '':
                pass
            else:
                file_dict['crtime'] = datetime.datetime.utcfromtimestamp(float(file[17])).isoformat()
            
            #get last access time
            if file[18] == '0' or file[18] == '':
                pass
            else:
                file_dict['atime'] = datetime.datetime.utcfromtimestamp(float(file[18])).isoformat()
            
            #get last modified time
            if file[19] == '0' or file[19] == '':
                pass
            else:
                file_dict['mtime'] = datetime.datetime.utcfromtimestamp(float(file[19])).isoformat()
            
            file_dict['size'] = file[15]
            file_dict['part'] = file[2]
            file_dict['id'] = file[0]
            file_dict['meta_type'] = file[12]
            
            if file[12] == '4':
                file_dict['name_type'] = 'c'
            
            elif file[12] == '2':
                file_dict['name_type'] = 'd'
            
            elif file[12] == '3':
                file_dict['name_type'] = 'p'
            
            elif file[12] == '1':
                file_dict['name_type'] = 'r'
            
            elif file[12] == '6':
                file_dict['name_type'] = 'l'
            
            elif file[12] == '5':
                file_dict['name_type'] = 'b'
            
            elif file[12] == '8':
                file_dict['name_type'] = 'h'
            
            elif file[12] == '7':
                file_dict['name_type'] = 's'
            
            elif file[12] >= '10':
                file_dict['name_type'] = 'v'
            
            elif file[12] == '9':
                file_dict['name_type'] = 'w'
                
            else:
                file_dict['name_type'] = '-'
                
            if file[13] == '1':
                file_dict['alloc'] = file[13]
            else:
                file_dict['alloc'] = '0'
            file_dict['inode'] = file[6]
            file_dict['mode'] = file[20]
            file_dict['uid'] = file[21]
            file_dict['gid'] = file[22]
            file_dict['md5'] = file[23]
            
            #check to see if any metadata elements used; if so, 'used' is true; otherwise false
            for u in file_dict.values():
                if len(u) > 0:
                    file_dict['used'] = '1'
                    break
                else:
                    file_dict['used'] = '0'
            
            #figure out byte runs; get the obj_id for the files and associated slack space
            id_list = []
            
            if file[6] == '':
                id_list = [file[0]]
            else:
                sql_byte_cmd = 'sqlite3 %s -newline " " "SELECT obj_id from tsk_files WHERE meta_addr = %s;"' % (tsk_db, file[6])
                id_list = []
                id_list = subprocess.check_output(sql_byte_cmd, shell=True).split()
                
                                
                #get size (in bytes) of slack space so that we can accurately represent len of files in DFXML
                sql_slack_cmd = 'sqlite3 %s -newline " " "SELECT size from tsk_files WHERE meta_addr = %s and type = 7;"' % (tsk_db, file[6])
                
                slack_list = []
                slack_list = map(int, subprocess.check_output(sql_slack_cmd, shell=True).split())
                
                if len(slack_list) == 0:
                    slack_list = [0]
                        
            #now loop through tsk_file_layout (skipping header)
            bytestart_list = []
            bytelen_list = []
            
            for run in data_tsk_file_layout[1:]:
                #check to see if the obj_ids are in the first column of tsk_file_layout; if so, add byte start and byte len info to lists
                if id_list[0] == run[0] :
                    bytestart_list.append(int(run[1]))
                    bytelen_list.append(int(run[2]))
                if len(id_list) > 1:
                    if id_list[1] == run[0]:
                        bytestart_list.append(int(run[1]))
                        bytelen_list.append(int(run[2]))
                            
            if len(bytestart_list) > 0:
                file_dict['bytelen_list'] = bytelen_list
                file_dict['bytestart_list'] = bytestart_list
                file_dict['slack_list'] = slack_list
            
            #append current dictionary to master list of file info
            file_list.append(file_dict)


    print '\n\nGenerating DFXML from disk image metadata...'
    
    attr_qname = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    dfxml_namespace = 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML'
    dfxml_ns = "{%s}" % dfxml_namespace
    dc_namespace = 'http://purl.org/dc/elements/1.1/'
    dc = "{%s}" % dc_namespace
    NSMAP = {'dc' : dc_namespace, 
             'xsi': "http://www.w3.org/2001/XMLSchema-instance", 
             None : dfxml_namespace}

    dfxml = ET.Element("dfxml", version="1.0", nsmap=NSMAP)
    
    metadata = ET.SubElement(dfxml, "metadata")
    
    dctype = ET.SubElement(metadata, dc + "type")
    dctype.text = dfxml_dict['type']
    
    creator = ET.SubElement(dfxml, 'creator')
    
    program = ET.SubElement(creator, 'program')
    program.text = dfxml_dict['creator_program']
    
    execution_environment = ET.SubElement(creator, 'execution_environment')
    
    #command_line = ET.SubElement(execution_environment, 'command_line')
    #command_line.text = dfxml_dict['cmd_line']
    
    start_time = ET.SubElement(execution_environment, 'start_time')
    start_time.text = dfxml_dict['start_time']
    
    sourceDir = ET.SubElement(dfxml, 'source')
    
    image_filename = ET.SubElement(sourceDir, 'image_filename')
    image_filename.text = bdpl_vars()['imagefile']
    
    volume = ET.SubElement(dfxml, 'volume', offset='%s' % dfxml_dict['vol_offset'])
    
    partition_offset = ET.SubElement(volume, 'partition_offset')
    partition_offset.text = dfxml_dict['part_offset']
    
    sector_size = ET.SubElement(volume, 'sector_size')
    sector_size.text = dfxml_dict['sect_size']
    
    block_size = ET.SubElement(volume, 'block_size')
    block_size.text = dfxml_dict['blk_size']
    
    ftype = ET.SubElement(volume, 'ftype')
    ftype.text = dfxml_dict['ftype']
    
    ftype_str = ET.SubElement(volume, 'ftype_str')
    ftype_str.text = dfxml_dict['ftype_str']
    
    block_count = ET.SubElement(volume, 'block_count')
    block_count.text = dfxml_dict['blk_ct']
    
    first_block = ET.SubElement(volume, 'first_block')
    first_block.text = dfxml_dict['fst_blk']
    
    last_block = ET.SubElement(volume, 'last_block')
    last_block.text = dfxml_dict['lst_blk']
    
    for f in file_list:
        fileobject = ET.SubElement(volume, 'fileobject')
        parent_object = ET.SubElement(fileobject, 'parent_object')
        po_inode = ET.SubElement(parent_object, 'inode')
        po_inode.text = f['parent_inode']
        
        filename = ET.SubElement(fileobject, 'filename')
        filename.text = f['filename']
        
        partition = ET.SubElement(fileobject, 'partition')
        partition.text = f['part']
        
        fo_id = ET.SubElement(fileobject, 'id')
        fo_id.text = f['id']
        
        name_type = ET.SubElement(fileobject, 'name_type')
        name_type.text = f['name_type']
        
        filesize = ET.SubElement(fileobject, 'filesize')
        filesize.text = f['size']
        
        alloc = ET.SubElement(fileobject, 'alloc')
        alloc.text = f['alloc']
        
        inode = ET.SubElement(fileobject, 'inode')
        inode.text = f['inode']
        
        meta_type = ET.SubElement(fileobject, 'meta_type')
        meta_type.text = f['meta_type']
        
        mode = ET.SubElement(fileobject, 'mode')
        mode.text = f['mode']
        
        nlink = ET.SubElement(fileobject, 'nlink')
        
        uid = ET.SubElement(fileobject, 'uid')
        uid.text = f['uid']
        
        gid = ET.SubElement(fileobject, 'gid')
        gid.text = f['gid']
        
        if 'ctime' in f:
            mtime = ET.SubElement(fileobject, 'ctime')
            mtime.text = f['ctime']
        
        if 'crtime' in f:
            mtime = ET.SubElement(fileobject, 'crtime')
            mtime.text = f['crtime']
            
        if 'atime' in f:
            mtime = ET.SubElement(fileobject, 'atime')
            mtime.text = f['atime']
            
        if 'mtime' in f:
            mtime = ET.SubElement(fileobject, 'mtime')
            mtime.text = f['mtime']
        
        if 'bytestart_list' in f:
            byte_runs = ET.SubElement(fileobject, 'byte_runs')
            
            #use lists to calculate byte runs
            i = 0
                        
            for item in f['bytestart_list']:
                fs_os = str(f['bytestart_list'][i])
                img_os = str(f['bytestart_list'][i])
                
                #first byte run will have a file/fs offset of 0; all others will have byte_start as reported in tsk_file_layout 
                if i == 0:
                    file_os = '0'
                else:
                    file_os = str(sum(f['bytelen_list'][:i]))
                
                #final len will need to subtract size of slack space to accurately report file size
                if i == (len(f['bytestart_list']) - 1):
                    bytelen = str(f['bytelen_list'][i] - sum(f['slack_list']))
                else:
                    bytelen = str(f['bytelen_list'][i])
                
                byteattributes = {"file_offset":'%s' % file_os, "fs_offset":'%s' % fs_os, "img_offset":'%s' % img_os, "len":'%s' % bytelen}
                
                byte_run = ET.SubElement(byte_runs, 'byte_run', byteattributes)
            
                i += 1
            
        hashdigest = ET.SubElement(fileobject, 'hashdigest', type='md5')
        hashdigest.text = f['md5']

    tree = ET.ElementTree(dfxml)
        
>>>>>>> 2f71f5a312468d05196e80ee78de61dcd79fc184
    tree.write(dfxml_output, pretty_print=True, xml_declaration=True, encoding="utf-8")  