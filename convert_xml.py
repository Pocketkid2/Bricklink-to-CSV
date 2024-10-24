import csv
import json
import xml.etree.ElementTree as ET
import argparse
import os

from colors import colors

def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    parts = []

    for item in root:
        part = {}
        for data in item:
            if data.tag == 'ITEMID':
                part['elementId'] = data.text
            if data.tag == 'COLOR':
                part['elementId'] += data.text
                #part['color'] = colors[int(part['color_id'])]
            if data.tag == 'MINQTY':
                part['quantity'] = data.text
        
        parts.append(part)
    
    return parts

def export_csv(data, path):
    fields = ['elementId', 'quantity']

    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
  
        writer.writeheader()
  
        writer.writerows(data)

def export_json(data, path):
    with open(path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Process XML and export to CSV or JSON.')
    parser.add_argument('input_xml', help='Path to the input XML file')
    parser.add_argument('output_file', help='Path to the output file')
    args = parser.parse_args()

    data = parse_xml(args.input_xml)
    
    _, ext = os.path.splitext(args.output_file)
    if ext == '.csv':
        export_csv(data, args.output_file)
    elif ext == '.json':
        export_json(data, args.output_file)
    else:
        raise ValueError("Output file must have a .csv or .json extension")

if __name__ == '__main__':
    main()