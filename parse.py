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
    non_parts = set()
    total_quantity = 0
    for item in root:
        part = {}
        for data in item:
            if data.tag == 'ITEMTYPE':
                part['type'] = data.text
            elif data.tag == 'ITEMID':
                part['design_id'] = data.text
                if part['type'] == 'P':
                    unique_designs.add(data.text)
                else:
                    logging.warning(f"Found non-part design ID {data.text} in {path}")
                    non_parts.add(data.text)
            elif data.tag == 'COLOR':
                part['color_id'] = data.text
            elif data.tag == 'MAXPRICE':
                part['price'] = data.text
            elif data.tag == 'MINQTY':
                part['quantity'] = data.text
                if part['type'] == 'P':
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
    logging.info(f"Found {len(non_parts)} non-part design IDs in {path}")
    return parts


def parse_cart(path):
    """
    Create cart lot data from a BrickLink .cart file.

    Args:
        path (str): The file path to the BrickLink .cart file

    Returns:
        list of dict: The cart lot data extracted from the .cart file
    """
    with open(path, 'r') as file:
        cart_string = file.read().strip()
        bytes_data = bytes.fromhex(cart_string)
        ascii_data = bytes_data.decode('ascii')
        records = ascii_data.strip().split('\n')
        cart_items = []
        for record in records:
            parts = record.split(':')
            if len(parts) >= 4:
                item = {
                    # 'prefix': parts[0],
                    'store_id': parts[1],
                    'lot_id': parts[2],
                    'quantity': int(parts[3])
                }
                cart_items.append(item)
        return cart_items
