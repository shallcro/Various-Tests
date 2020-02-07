from lxml import etree

attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
PREMIS_NAMESPACE = "http://www.loc.gov/premis/v3"
PREMIS = "{%s}" % PREMIS_NAMESPACE
NSMAP = {'premis' : PREMIS_NAMESPACE,
         "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

premis_path = "C:/temp/30000149745501-premis.xml" 

parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(premis_path, parser=parser)
root = tree.getroot()
events = tree.xpath("//premis:event", namespaces=NSMAP)

premis_list = []

for e in events:
    temp_dict = {}
    temp_dict['eventType'] = e.findtext('./premis:eventType', namespaces=NSMAP)
    temp_dict['eventOutcomeDetail'] = e.findtext('./premis:eventOutcomeInformation/premis:eventOutcome', namespaces=NSMAP)
    temp_dict['timestamp'] = e.findtext('./premis:eventDateTime', namespaces=NSMAP)
    temp_dict['eventDetailInfo'] = e.findall('./premis:eventDetailInformation/premis:eventDetail', namespaces=NSMAP)[0].text
    temp_dict['eventDetailInfo_additional'] = e.findall('./premis:eventDetailInformation/premis:eventDetail', namespaces=NSMAP)[1].text
    temp_dict['linkingAgentIDvalue'] = e.findall('./premis:linkingAgentIdentifier/premis:linkingAgentIdentifierValue', namespaces=NSMAP)[1].text
    premis_list.append(temp_dict)
    
print(premis_list)

term = 'Sensitive data scan'
command = 'bulk_extractor -x aes -x base64 -x elf -x exif -x gps -x hiberfile -x httplogs -x json -x kml -x net -x pdf -x sqlite -x winlnk -x winpe -x winprefetch -S ssn_mode=2 -o "Z:\\UAC\\ingest\\20190225\\30000149745501\\bulk_extractor" -R "Z:\\UAC\\ingest\\20190225\\30000149745501\\files" > "Z:\\UAC\\ingest\\20190225\\30000149745501\\metadata\\logs\\bulkext-log.txt"'
version = 'bulk_extractor 1.6.0-dev\n'

for dic in premis_list:
    if dic['eventOutcomeDetail'] == '0':
        print('string')
    elif dic['eventOutcomeDetail'] == 0:
        print('int')