from argparse import ArgumentParser, RawTextHelpFormatter
import os
import openpyxl
import datetime
#from bdpl_ingest import *
import pickle
import shutil
from lxml import etree
import glob

def main():
    #set up arg parser so user is required to add shipment directory
    parser = ArgumentParser(
        description='This script prepares specified content for deposit to Media Collections Online from the IUL BDPL.',
        formatter_class=RawTextHelpFormatter
    )
    
    parser.add_argument(
        '-prep', 
        help='Prep metadata and files to deposit to MCO',
        action='store_true'
    )
    
    parser.add_argument(
        '-move', 
        help='Move files to MCO dropbox',
        action='store_true'
    )
    
    parser.add_argument(
        'unit_name',
        help='Unit abbreviation',
    )

    parser.add_argument(
        'shipmentDate',
        help='Shipment date',
    )
    
    parser.add_argument(
        '-mco', '--mco_dropbox',
        help='Path to MCO dropbox',
    )
    args = vars(parser.parse_args())
    
    if args['move'] == args['prep']:
        parser.error('\nScript can only be used to prep content OR to move files.  Make sure you have selected appropriate option.')
    
    #make sure valid unit name and shipment date were entered
    #if not all(args.get(k) for k in ('unit_name', 'shipmentDate')):
    
    
    if not all(k in args for k in ('unit_name', 'shipmentDate')):
        print('oh no!')
    
    
    
    # if all(args.get(k) for k in ('unit_name', 'shipmentDate')) and not args.get('mco_dropbox'):
        # print('two out of three')
    # elif all(args.get(k) for k in ('unit_name', 'shipmentDate', 'mco_dropbox')):
        # print('all three')
    # else:
         # parser.error('\nThis script has two options:\n\t(a) Prepare specified content for deposit to Media Collections Online (MCO)\n\t(b) Move content from Scandium to the MCO dropbox.'
    
    print(args)
    

if __name__ == "__main__":
    main()