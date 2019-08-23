import urllib.request
import os
import sys
import zipfile
import shutil
import subprocess
import progressbar
import time

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()



def main():
    # global pbar, downloaded
    # pbar = None
    # downloaded = 0
    
    #get new version of ClamAV
    version = input('\nEnter new ClamAV version (number only): ')

    file = "https://www.clamav.net/downloads/production/clamav-%s-win-x64-portable.zip" % version

    print('\nChecking %s...' % file)

    #make sure the URL works; exit if not.  NOTE: may need to change hard-coded URL
    try:
        urllib.request.urlopen(file)
        print('\nURL looks good...')
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(e, '\n\n%s may be incorrect; check ClamAV download URL')
        sys.exit(1)

    filename = os.path.basename(file)

    #get username so we can download to local Downloads folder
    username = os.getlogin()
    downloads = os.path.join('C:\\Users', username, 'Downloads')
    dest = os.path.join(downloads, filename)

    if os.path.exists(dest):
        os.remove(dest)

    #download zip file
    print('\nDownloading new version of ClamAV...\n')
    urllib.request.urlretrieve(file, dest, reporthook)


    #extract contents of zip
    print('\n\nExtracting contents from zip file...')
    extract_dest = os.path.join(downloads, 'clamav')
    if os.path.exists(extract_dest):
        shutil.rmtree(extract_dest)
        
    with zipfile.ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(extract_dest)
        
    #copy our freshclam.conf file
    shutil.copy('C:/BDPL/resources/clamav/freshclam.conf', extract_dest)

    #remove old clamav
    print('\nRemoving old version of ClamAV...')
    bdpl_dest = 'C:/BDPL/resources/clamav'
    shutil.rmtree(bdpl_dest)

    #copy over new version
    print('\nMoving new version to %s...' % bdpl_dest)
    shutil.move(extract_dest, 'C:/BDPL/resources')

    #run freshclam to update definitions
    print('\nUpdating antivirus definitions...\n')
    os.chdir(bdpl_dest)
    subprocess.check_output('freshclam', shell=True, text=True)
    
    print('\nAll done!')
    
if __name__ == '__main__':
    main()