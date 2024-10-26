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
        unique_elements.add(f"{part['design_id']}/{part['color_id']}")
        parts.append(part)
    logging.info(f"Found {len(unique_designs)} unique designs, "
                 f"{len(unique_elements)} unique elements, "
                 f"with {total_quantity} total quantity in {path}")
    return parts
