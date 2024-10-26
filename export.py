"""
Export.

This module provides functions to export partslist data to CSV and JSON files.
"""

import csv
import json
import logging


def export_csv(data, path):
    """
    Save partslist data to a CSV file.

    Args:
        data (list of dict): The partslist data to be exported.
        path (str): The file path where the CSV file will be saved.
    """
    fields = ['elementId', 'quantity']
    with open(path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Exported {len(data)} entries to {path}")


def export_json(data, path):
    """
    Save partslist data to a JSON file.

    Args:
        data (list of dict): The partslist data to be exported.
        path (str): The file path where the JSON file will be saved.
    """
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    logging.info(f"Exported {len(data)} entries to {path}")


def export_xml(data, path):
    """
    Save partslist data to an XML file.

    Args:
        data (list of dict): The partslist data to be exported.
        path (str): The file path where the XML file will be saved.
    """
    with open(path, 'w') as xml_file:
        xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        xml_file.write('<INVENTORY>\n')
        for entry in data:
            xml_file.write('<ITEM>\n')
            xml_file.write('<ITEMTYPE>P</ITEMTYPE>\n')
            xml_file.write(f'<ITEMID>{entry['design_id']}</ITEMID>\n')
            xml_file.write(f'<COLOR>{entry['color_id']}</COLOR>\n')
            xml_file.write('<MAXPRICE>-1.0000</MAXPRICE>\n')
            xml_file.write(f'<MINQTY>{entry['quantity']}</MINQTY>\n')
            xml_file.write('<CONDITION>X</CONDITION>\n')
            xml_file.write('<NOTIFY>N</NOTIFY>\n')
            xml_file.write('</ITEM>\n')
        xml_file.write('</INVENTORY>\n')
    logging.info(f"Exported {len(data)} entries to {path}")