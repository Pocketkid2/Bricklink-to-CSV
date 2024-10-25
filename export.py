import csv
import json
import logging


# Save partslist data to CSV file
def export_csv(data, path):
    fields = ['elementId', 'quantity']
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Exported {len(data)} entries to {path}")


# Save partslist data to JSON file
def export_json(data, path):
    with open(path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    logging.info(f"Exported {len(data)} entries to {path}")