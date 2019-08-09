'''script to test DFXML parsing'''

from lxml import etree


dfxml = input('Enter Python-appropriate path to DFXML file: ')

tree = etree.parse(dfxml)

# find all the <fileobject> elements
file_objects = tree.xpath("//fileobject")

filenames_and_hashdigest_dict = {}

filesizes = []

# #for md5deep dfxml
# if tree.getroot().tag == "{http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML}dfxml":
    # for file_object in file_objects:
        # filesize = file_object.findtext("./filesize")
        # filesizes.append(int(filesize))

# #for fiwalk dfxml
# elif tree.getroot().tag == 'fiwalk':

    # for file_object in file_objects:
        # # check values of <name_type> and <alloc>
        # if file_object.findtext("./name_type") == "r" and file_object.findtext("./alloc") == "1":
            # filesize = file_object.findtext("./filesize")
            # filesizes.append(int(filesize))

#else:
    

# iterate through the <fileobject> elements
for file_object in file_objects:
    # check values of <name_type> and <alloc>
    if file_object.findtext("./name_type") == "r" and file_object.findtext("./alloc") == "1":
        # grab the values of <filename> and <hashdigest>
        filename = file_object.findtext("./filename")
        hashdigest = file_object.findtext("./hashdigest[@type='md5']")
        # then, do whatever with them! Print them, add them to a dictionary, etc.
        print("Filename: {}, Hash: {}".format(filename, hashdigest))
        filenames_and_hashdigest_dict[filename] = hashdigest

print(filenames_and_hashdigest_dict)