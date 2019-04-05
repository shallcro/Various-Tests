from lxml import etree as ET

barcode = 'jjjj'

attr_qname = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

PREMIS_NAMESPACE = "http://www.loc.gov/premis/v3"

PREMIS = "{%s}" % PREMIS_NAMESPACE

NSMAP = {'premis' : PREMIS_NAMESPACE,
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

root = ET.Element(PREMIS + 'premis', {attr_qname: "http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd"}, version="3.0", nsmap=NSMAP)

    object = ET.SubElement(root, PREMIS + 'object', attrib={ET.QName(NSMAP['xsi'], 'type'): 'premis:file'})
    objectIdentifier = ET.SubElement(object, PREMIS + 'objectIdentifier')
    objectIdentifierType = ET.SubElement(objectIdentifier, PREMIS + 'objectIdentifierType')
    objectIdentifierType.text = 'local'
    objectIdentifierValue = ET.SubElement(objectIdentifier, PREMIS + 'objectIdentifierValue')
    objectIdentifierValue.text = barcode.get()
    objectCharacteristics = ET.SubElement(object, PREMIS + 'objectCharacteristics')
    compositionLevel = ET.SubElement(objectCharacteristics, PREMIS + 'compositionLevel')
    compositionLevel.text = '0'
    format = ET.SubElement(objectCharacteristics, PREMIS + 'format')
    formatDesignation = ET.SubElement(format, PREMIS + 'formatDesignation')
    formatName = ET.SubElement(formatDesignation, PREMIS + 'formatName')
    formatName.text = 'Tape Archive Format'
    formatRegistry = ET.SubElement(format, PREMIS + 'formatRegistry')
    formatRegistryName = ET.SubElement(formatRegistry, PREMIS + 'formatRegistryName')
    formatRegistryName.text = 'PRONOM'
    formatRegistryKey = ET.SubElement(formatRegistry, PREMIS + 'formatRegistryKey')
    formatRegistryKey.text = 'x-fmt/265' 



event = ET.SubElement(root, PREMIS + 'event')
eventID = ET.SubElement(event, PREMIS + 'eventIdentifier')
eventIDtype = ET.SubElement(eventID, PREMIS + 'eventIdentifierType', attrib={ET.QName(NSMAP['xsi'], 'type'): 'premis:file'})
eventIDtype.text = 'UUID'
premis_tree = ET.ElementTree(root)

premis_path = 'C:\\temp\\premis.xml'

premis_tree.write(premis_path, pretty_print=True, xml_declaration=True, encoding="utf-8")