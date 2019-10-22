'''
script to pull stats from BDPL spreadsheets currently in process
'''

import openpyxl
import os
import glob
import collections
import math
import subprocess

def convert_size(size):
    # convert size to human-readable form
    if (size == 0):
        return '0 bytes'
    size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p)
    s = str(s)
    s = s.replace('.0', '')
    return '%s %s' % (s,size_name[i])

def main():

    #add any other temp/work folders, if they are present
    working_dirs = ['TEST', 'media-images', 'bdpl_transfer_lists', 'Ripstation']
    
    #assumes that bdpl\workspace is mapped to Z:\ drive; change if needed. Get a list of projects from that location. 
    workspace = 'Z:\\'
    projects = os.listdir('Z:/')
    
    #remove any working_dirs from list
    projects = [dir for dir in projects if dir not in working_dirs]
    
    #specify a location for output file
    output = "C:/BDPL/current_stats.txt"
    if os.path.exists(output):
        os.remove(output)

    stats = {'total_size' : 0, 'total_files' : 0, 'total_items' : 0}
    
    for project in projects:
    
        with open(output, 'a') as f:
            f.write('\n\n%s\n' % project)
        
        home_dir = os.path.join(workspace, project, 'ingest')
        
        if not os.path.exists(home_dir):
            continue
        
        stats[project] = []
        
        for shipment in os.listdir(home_dir):
        
            
            temp = {}
                       
            if glob.glob(os.path.join(home_dir, shipment, '*.xlsx')):
                spreadsheet = glob.glob(os.path.join(home_dir, shipment, '*.xlsx'))[0]
            else:
                continue
            
            spreadsheet_name = os.path.basename(spreadsheet)
            
            if os.path.exists(os.path.join(workspace, project, 'completed_shipments', spreadsheet_name)):
                continue
            
            wb = openpyxl.load_workbook(spreadsheet)
            
            ws = wb['Appraisal']
            
            temp['shipment'] = shipment
            temp['raw_formats'] = []
            temp['size'] = []
            temp['item_count'] = 0
            temp['file_count'] = 0
            iterrows = ws.iter_rows()
            next(iterrows)
            
            for row in iterrows:
                if row[13].value == 'Success':
                    temp['item_count'] += 1
                    temp['file_count'] += int(row[17].value)
                    temp['raw_formats'].append(row[6].value.split(' (')[0].lower().replace(' ', '').replace('?', ''))
                    temp['size'].append(row[15].value)
                    
            #tally our sizes
            final_size = 0
            for unit in ["bytes", "KB", "MB", "GB", "TB"]:
                subgroup = [x for x in temp['size'] if unit in x]
                if len(subgroup) > 0:
                    for item in subgroup:
                        if 'bytes' in item:
                            volume = int(item.split(' ')[0])
                        elif 'KB' in item:
                            volume = int(item.split(' ')[0]) * 1000
                        elif 'MB' in item:
                            volume = int(item.split(' ')[0]) * 1000000
                        elif 'GB' in item:
                            volume = int(item.split(' ')[0]) * 1000000000
                        elif 'GB' in item:
                            volume = int(item.split(' ')[0]) * 1000000000000
                        final_size += volume
            temp['size'] = final_size
            
            format_count = collections.Counter(temp['raw_formats'])
            temp['final_formats'] = dict(format_count)
            
            with open(output, 'a') as f:
                f.write('\n\tShipment: %s\n' % temp['shipment'])
                f.write('\t\tItem count: %s\n' % temp['item_count'])
                f.write('\t\tFile count: %s\n' % temp['file_count'])
                f.write('\t\tSize (in bytes): %s (%s)\n' % (temp['size'], convert_size(temp['size'])))
                f.write('\t\tSource formats:\n')
                for key, value in temp['final_formats'].items():
                    f.write('\t\t\t%s: %s\n' % (key, value))
                  
            stats[project].append(temp)
            
        total_unit_items = 0
        total_unit_count = 0
        total_size = 0
        total_formats = []
        
        for totals in stats[project]:
            total_unit_count += totals['file_count']
            total_unit_items += totals['item_count']
            total_formats = total_formats + totals['raw_formats']
            total_size += totals['size']
        
        format_count = collections.Counter(total_formats)
        
        with open(output, 'a') as f:
            f.write('\n\tTOTALS:\n')
            f.write('\t\tTotal items: %s\n' % total_unit_items)
            f.write('\t\tTotal files: %s\n' % total_unit_count)
            f.write('\t\tTotal size: %s (%s)\n' % (total_size, convert_size(total_size)))
            f.write('\t\tTotal format tallies:\n')
            for key, value in dict(format_count).items():
                f.write('\t\t\t%s: %s\n' % (key, value))
        
        stats['total_files'] += total_unit_count
        stats['total_items'] += total_unit_items
        stats['total_size'] += total_size
        
    with open(output, 'a') as f:
        f.write('\n\nGRAND TOTALS FOR CURRENT WORK:\n')
        f.write('\tItems: %s\n' % stats['total_items'])
        f.write('\tFiles: %s\n' % stats['total_files'])
        f.write('\tSize: %s (%s)\n' % (stats['total_size'], convert_size(stats['total_size'])))
        
    print('\n\nStatistics for current BDPL work (not deposited to SDA) saved to %s' % output)
    
    cmd = 'notepad %s' % output
    subprocess.call(cmd)

if __name__ == '__main__':
    main()       
                       
        