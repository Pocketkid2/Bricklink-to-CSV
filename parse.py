import logging
import xml.etree.ElementTree as ET


# Create partslist data from XML file
def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    parts = []
    unique_designs = set()
    unique_elements = set()
    total_quantity = 0
    for item in root:
        part = {}
        for data in item:
            if data.tag == 'ITEMID':
                part['design_id'] = data.text
                unique_designs.add(data.text)
            elif data.tag == 'COLOR':
                part['color_id'] = data.text
            elif data.tag == 'MINQTY':
                part['quantity'] = data.text
                total_quantity += int(data.text)
            unique_elements.add(f"{part['design_id']}/{part['color_id']}")
        parts.append(part)
    logging.info(f"Found {unique_designs} unique designs, {unique_elements} unique elements, with {total_quantity} total quantity in {path}")
    return parts