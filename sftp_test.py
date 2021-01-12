#https://andrewrgoss.com/2016/ssh-keys-with-putty-and-cygwin-for-windows/ for how to create a private key and then share with a server

import paramiko
import stat
#paramiko.util.log_to_file("paramiko.log")

def splitall(path):
    allparts = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


#start pageant
#"C:\Program Files\PuTTY\pageant.exe" C:\BDPL\keys\scandium-key.ppk

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# host = 'beryllium.dlib.indiana.edu'
# port = 22
# user = 'micshall'
# ssh.connect(host, port=port, username=user, allow_agent=True)
# stdin,stdout,stderr = ssh.exec_command("ps -ef")


# ssh = paramiko.SSHClient()
# ssh.connect(host, username='user', allow_agent=True)
# sftp = ssh.open_sftp()

# keyfilepath = 'C:/BDPL/keys/scandium-key.ppk'
# key = paramiko.RSAKey.from_private_key(keyfilepath)

# Open a transport
host,port = "beryllium.dlib.indiana.edu",22
try:
    transport = paramiko.Transport((host,port))
except:
    print('WHOOPS')
# Auth    
username = input('Username: ')
password = input('Password: ')

try:
    transport.connect(None, username, password)

    # Go!    
    sftp = paramiko.SFTPClient.from_transport(transport)

except:
    print('WHOOPS part II')

# Download
# filepath = "/etc/passwd"
# localpath = "/home/remotepasswd"
# sftp.get(filepath,localpath)

# Upload
# filepath = "foo/bar/FFFFF.txt"
# localpath = "C:/tools/FFFFF.txt"
# sftp.put(localpath,filepath)

# try:
    # sftp.mkdir('baz')
# except IOError:
    # print('Oh no!')

if sftp:
    print('connected')
else:
    print('not connected')


sftp.mkdir('mike/was/here')
    
    # dirlist = sftp.listdir('/srv/avalon/dropbox')
    # print(sorted(dirlist))
    # # for d in sorted(dirlist):
        # # print(d)
        
    # #check attributes
    # for fileattr in sftp.listdir_attr('/srv/avalon/dropbox'):  
            # if stat.S_ISDIR(fileattr.st_mode):
                # print(fileattr.filename)

    # ls = [fileattr.filename for fileattr in sftp.listdir_attr('/srv/avalon/dropbox') if stat.S_ISDIR(fileattr.st_mode)]

    # print(sorted(ls))


# Close
if sftp: 
    sftp.close()
else:
    print('No SFTP to close')
    
if transport: 
    transport.close()
else:
    print('No transport to close')