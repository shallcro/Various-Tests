import os
import subprocess
import openpyxl
import glob

'''Run for earlier BDPL shipments where entire Bulk Extractor output was not retained for appraisal.'''

def main():

    while True:

        shipment = input('\nFull path to shipment folder: ')
        shipment = shipment.replace('"', '').rstrip()
        
        if not os.path.exists(shipment):
            print('Shipment folder not recognized; enclose in quotes and use "/".\n')
            continue

        #check on spreadsheet before we go any further; the following will help make sure that a hidden temp file doesn't foul things up
        spreadsheets = list(set(glob.glob(os.path.join(shipment, '*.xlsx'))) - set(glob.glob(os.path.join(shipment, '~*.xlsx'))))
        if len(spreadsheets) !=1:
            print('\nWARNING: cannot identify shipment spreadsheet.  Please check directory to make sure .XLSX file is present.')
            print(spreadsheets)
            continue
        else:
            spreadsheet = spreadsheets[0]
            
        break
        
    #pii_list = ['EMAIL', 'TELEPHONE NOs', 'ACCOUNT NOs', 'CCNs']
    pii_list = ['ACCOUNT NOs', 'CCNs']
    
    #set shipment directory as current working directory
    os.chdir(shipment) 
     
    #open shipment workbook
    wb = openpyxl.load_workbook(spreadsheet)
    ws = wb['Appraisal']
    
    iterrows = ws.iter_rows()
    next(iterrows)
    
    for row in iterrows:

        barcode = str(row[0].value)
        target = os.path.join(shipment, barcode, 'files')
        bulkext_dir = os.path.join(shipment, barcode, 'bulk_extractor')
        
        if not os.path.exists(target):
            continue
        
        if not row[23].value is None:
            
            if [p for p in pii_list if p in row[23].value]:
            
                if os.path.exists(os.path.join(bulkext_dir, 'report.xml')):
                    print('\n\n%s already has b_e report' % barcode)
                    continue
                
                else:
                    print('\nCreating b_e report for', barcode)
                    
                    #use default command with buklk_extractor; individuak could implement changes to use 'find' scanner at a later date
                    bulkext_command = 'bulk_extractor -x aes -x base64 -x elf -x exif -x gps -x hiberfile -x httplogs -x json -x kml -x net -x pdf -x sqlite -x vcard -x winlnk -x winpe -x winprefetch -S ssn_mode=2 -o "%s" -R "%s"' % (bulkext_dir, target)
                    
                    try:
                        exitcode = subprocess.call(bulkext_command, shell=True, text=True)
                        print('\n\tCompleted bulk_extractor operation.')
                    except subprocess.CalledProcessError as e:
                        print('\n\tError:', e)
                    
if __name__ == '__main__':
    main()       
        
        