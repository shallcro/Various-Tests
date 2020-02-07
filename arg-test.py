from argparse import ArgumentParser, RawTextHelpFormatter
import os
#from bdpl_ingest import *

def main():
    #set up arg parser so user is required to add shipment directory
    parser = ArgumentParser(
        description='This script prepares specified content for deposit to Media Collections Online from the IUL BDPL.',
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        '-unit', 
        help='Unit abbreviation',
    )

    parser.add_argument(
        '-shipmentDate', 
        help='Unit abbreviation',
    )
    
    args = vars(parser.parse_args())

    if not args.get('unit') or not args.get('shipmentDate'):
        parser.error('\n\nScript requires a valid unit abbreviation and associated shipment date.')
    else:
        folders = bdpl_folders(unit_name, shipmentDate)
        ship_dir = folders['ship_dir']
        
        if not os.path.exists(ship_dir):
            parser.error('\n\nScript requires a valid unit abbreviation and associated shipment date.')
        
        print('cool:', ship_dir)
        
    
        
if __name__ == "__main__":
    main()