"""
Parse.

This module provides functions to parse XML files and extract partslist data.
"""

import logging
import xml.etree.ElementTree as ET


def parse_xml(path):
    """
    Create partslist data from an XML file.

    Args:
        path (str): The file path to the XML file.

    Returns:
        list of dict: The partslist data extracted from the XML file.
    """
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
        design_id = part.get('design_id')
        color_id = part.get('color_id')
        if design_id and color_id:
            unique_elements.add(f"{design_id}/{color_id}")
            parts.append(part)
        else:
            logging.warning(f"Missing color_id for design_id {design_id} in {path}")
    logging.info(f"Found {len(unique_designs)} unique designs, "
                 f"{len(unique_elements)} unique elements, "
                 f"with {total_quantity} total quantity in {path}")
    return parts
