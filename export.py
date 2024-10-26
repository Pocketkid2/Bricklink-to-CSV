"""Export.

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
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
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
    with open(path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    logging.info(f"Exported {len(data)} entries to {path}")
