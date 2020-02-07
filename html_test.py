from lxml import etree
import uuid

doc = 'C:/temp/output.html'

html = etree.Element('html')
head = etree.SubElement(html, 'head')
style = etree.SubElement(head, 'style')
style.text = "table, th, td {padding: 10px; border: 1px solid black; border-collapse: collapse;}"
body = etree.SubElement(html, 'body')
h1 = etree.SubElement(body, 'h1')
h1.text ="Content Analysis"
table = etree.SubElement(body, 'table')
tr = etree.SubElement(table, 'tr')
th = etree.SubElement(tr, 'th')
th.text = 'Object'
th = etree.SubElement(tr, 'th')
th.text = 'Named Entities: People'
th = etree.SubElement(tr, 'th')
th.text = 'Named Entities: Organizations'
th = etree.SubElement(tr, 'th')
th.text = 'Named Entities: Locations'
th = etree.SubElement(tr, 'th')
th.text = 'Topic Modeling'
tr = etree.SubElement(table, 'tr')
td = etree.SubElement(tr, 'td')
td.text = '30002929302'
td = etree.SubElement(tr, 'td')
ul = etree.SubElement(td, 'ul')
ul.attrib['style'] = "list-style-type:none;"
a = etree.SubElement(ul, 'a')
a.attrib['href'] = './out/plot7.png'
a.attrib['target'] = "_blank"
li = etree.SubElement(a, 'li')
li.text ='Joe : 20'
li = etree.SubElement(a, 'li')
li.text ='Jim : 15'
li = etree.SubElement(a, 'li')
li.text ='Sue : 5'
td = etree.SubElement(tr, 'td')
td.text = 'USDA : 20</br>FCC : 15</br>IU : 5'
td = etree.SubElement(tr, 'td')
td.text = 'Indiana : 20\nOhio : 15\nBloomington : 5'
td = etree.SubElement(tr, 'td')
td.text = 'Professor, University, Tidy'

html_doc = etree.ElementTree(html)

html_doc.write(doc, method="html", pretty_print=True)

# item_barcode = '000'
    
# attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

# PREMIS_NAMESPACE = "http://www.loc.gov/premis/v3"

# PREMIS = "{%s}" % PREMIS_NAMESPACE

# NSMAP = {'premis' : PREMIS_NAMESPACE,
        # "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

# events = []

# #if our premis file already exists, we'll just delete it and write a new one

    
# root = etree.Element(PREMIS + 'premis', {attr_qname: "http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd"}, version="3.0", nsmap=NSMAP)

# object = etree.SubElement(root, PREMIS + 'object', attrib={etree.QName(NSMAP['xsi'], 'type'): 'premis:file'})
# objectIdentifier = etree.SubElement(object, PREMIS + 'objectIdentifier')
# objectIdentifierType = etree.SubElement(objectIdentifier, PREMIS + 'objectIdentifierType')
# objectIdentifierType.text = 'local'
# objectIdentifierValue = etree.SubElement(objectIdentifier, PREMIS + 'objectIdentifierValue')
# objectIdentifierValue.text = item_barcode
# objectCharacteristics = etree.SubElement(object, PREMIS + 'objectCharacteristics')
# compositionLevel = etree.SubElement(objectCharacteristics, PREMIS + 'compositionLevel')
# compositionLevel.text = '0'
# format = etree.SubElement(objectCharacteristics, PREMIS + 'format')
# formatDesignation = etree.SubElement(format, PREMIS + 'formatDesignation')
# formatName = etree.SubElement(formatDesignation, PREMIS + 'formatName')
# formatName.text = 'Tape Archive Format'
# formatRegistry = etree.SubElement(format, PREMIS + 'formatRegistry')
# formatRegistryName = etree.SubElement(formatRegistry, PREMIS + 'formatRegistryName')
# formatRegistryName.text = 'PRONOM'
# formatRegistryKey = etree.SubElement(formatRegistry, PREMIS + 'formatRegistryKey')
# formatRegistryKey.text = 'x-fmt/265' 


# event = etree.SubElement(root, PREMIS + 'event')
# eventID = etree.SubElement(event, PREMIS + 'eventIdentifier')
# eventIDtype = etree.SubElement(eventID, PREMIS + 'eventIdentifierType')
# eventIDtype.text = 'UUID'
# eventIDval = etree.SubElement(eventID, PREMIS + 'eventIdentifierValue')
# eventIDval.text = str(uuid.uuid4())

# eventType = etree.SubElement(event, PREMIS + 'eventType')
# eventType.text = '000'

# eventDateTime = etree.SubElement(event, PREMIS + 'eventDateTime')
# eventDateTime.text = '000'

# eventDetailInfo = etree.SubElement(event, PREMIS + 'eventDetailInformation')
# eventDetail = etree.SubElement(eventDetailInfo, PREMIS + 'eventDetail')
# eventDetail.text = '000'

# #include additional eventDetailInfo to clarify action; older transfers may not include this element, so skip if KeyError
# try:
    # eventDetailInfo = etree.SubElement(event, PREMIS + 'eventDetailInformation')
    # eventDetail = etree.SubElement(eventDetailInfo, PREMIS + 'eventDetail')
    # eventDetail.text = '000'
# except KeyError:
    # pass
    
# eventOutcomeInfo = etree.SubElement(event, PREMIS + 'eventOutcomeInformation')
# eventOutcome = etree.SubElement(eventOutcomeInfo, PREMIS + 'eventOutcome')
# eventOutcome.text = '000'
# eventOutDetail = etree.SubElement(eventOutcomeInfo, PREMIS + 'eventOutcomeDetail')
# eventOutDetailNote = etree.SubElement(eventOutDetail, PREMIS + 'eventOutcomeDetailNote')


# linkingAgentID = etree.SubElement(event, PREMIS + 'linkingAgentIdentifier')
# linkingAgentIDtype = etree.SubElement(linkingAgentID, PREMIS + 'linkingAgentIdentifierType')
# linkingAgentIDtype.text = 'local'
# linkingAgentIDvalue = etree.SubElement(linkingAgentID, PREMIS + 'linkingAgentIdentifierValue')
# linkingAgentIDvalue.text = 'IUL BDPL'
# linkingAgentRole = etree.SubElement(linkingAgentID, PREMIS + 'linkingAgentRole')
# linkingAgentRole.text = 'implementer'
# linkingAgentID = etree.SubElement(event, PREMIS + 'linkingAgentIdentifier')
# linkingAgentIDtype = etree.SubElement(linkingAgentID, PREMIS + 'linkingAgentIdentifierType')
# linkingAgentIDtype.text = 'local'
# linkingAgentIDvalue = etree.SubElement(linkingAgentID, PREMIS + 'linkingAgentIdentifierValue')
# linkingAgentIDvalue.text = '000'
# linkingAgentRole = etree.SubElement(linkingAgentID, PREMIS + 'linkingAgentRole')
# linkingAgentRole.text = 'executing software'
# linkingObjectID = etree.SubElement(event, PREMIS + 'linkingObjectIdentifier')
# linkingObjectIDtype = etree.SubElement(linkingObjectID, PREMIS + 'linkingObjectIdentifierType')
# linkingObjectIDtype.text = 'local'
# linkingObjectIDvalue = etree.SubElement(linkingObjectID, PREMIS + 'linkingObjectIdentifierValue')
# linkingObjectIDvalue.text = item_barcode

# premis_tree = etree.ElementTree(root)

# premis_tree.write(doc, pretty_print=True, xml_declaration=True, encoding="utf-8")