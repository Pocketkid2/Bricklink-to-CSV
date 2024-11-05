"""
Export.

This module provides functions to export partslist data to CSV and JSON files.
"""

import csv
import json
import logging


def export_csv(parts, path):
    """
    Save partslist data to a CSV file.

    Args:
        parts (list of dict): The partslist data to be exported.
        path (str): The file path where the CSV file will be saved.
    """
    fields = ['elementId', 'quantity']
    with open(path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(parts)
    logging.info(f"Exported {len(parts)} entries to {path}")


def export_json(parts, path):
    """
    Save partslist data to a JSON file.

    Args:
        parts (list of dict): The partslist data to be exported.
        path (str): The file path where the JSON file will be saved.
    """
    with open(path, 'w') as json_file:
        json.dump(parts, json_file, indent=4)
    logging.info(f"Exported {len(parts)} entries to {path}")


def export_xml(parts, path, condition='X'):
    """
    Save partslist data to an XML file.

    Args:
        parts (list of dict): The partslist data to be exported.
        path (str): The file path where the XML file will be saved.
    """
    if condition not in ['X', 'N', 'U']:
        raise ValueError("Condition must be one of 'X' (don't care), 'N' (new), or 'U' (used)")
    with open(path, 'w') as xml_file:
        xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        xml_file.write('<INVENTORY>\n')
        for part in parts:
            type = part['type']
            design_id = part['design_id']
            color_id = part['color_id']
            quantity = part['quantity']
            xml_file.write('<ITEM>\n')
            xml_file.write(f'<ITEMTYPE>{type}</ITEMTYPE>\n')
            xml_file.write(f'<ITEMID>{design_id}</ITEMID>\n')
            xml_file.write(f'<COLOR>{color_id}</COLOR>\n')
            xml_file.write('<MAXPRICE>-1.0000</MAXPRICE>\n')
            xml_file.write(f'<MINQTY>{quantity}</MINQTY>\n')
            xml_file.write(f'<CONDITION>{condition}</CONDITION>\n')
            xml_file.write('<NOTIFY>N</NOTIFY>\n')
            xml_file.write('</ITEM>\n')
        xml_file.write('</INVENTORY>\n')
    logging.info(f"Exported {len(parts)} entries to {path}")