import os
import csv
import json
import time
import argparse
from colors import colors_by_id
import xml.etree.ElementTree as ET
from grab_color_info import get_webpage_for_part
from grab_color_info import convert_table_to_dict
from grab_color_info import find_color_table_in_page


def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    parts = []
    for item in root:
        part = {}
        for data in item:
            if data.tag == 'ITEMID':
                part['design_id'] = data.text
            if data.tag == 'COLOR':
                part['color_id'] = data.text
            if data.tag == 'MINQTY':
                part['quantity'] = data.text
        parts.append(part)
    return parts


def map_design_and_color_to_element_id_array(dict):
    webpage = get_webpage_for_part(dict['design_id'])
    color_table = find_color_table_in_page(webpage)
    if not color_table:
        print("Could not find color table for design ID: ", dict['design_id'])
        return
    color_dict = convert_table_to_dict(color_table)
    color_id = int(dict['color_id'])
    element_ids = color_dict.get(color_id)
    return element_ids


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

    parts_input = parse_xml(args.input_xml)
    parts_output = []
    total_parts = len(parts_input)
    start_time = time.time()

    for i, part in enumerate(parts_input):
        part_start_time = time.time()
        element_ids = map_design_and_color_to_element_id_array(part)
        part_end_time = time.time()
        
        if element_ids:
            for element in element_ids:
                parts_output.append({'elementId': element, 'quantity': part['quantity']})
        
        elapsed_time = part_end_time - part_start_time
        average_time_per_part = (part_end_time - start_time) / (i + 1)
        remaining_parts = total_parts - (i + 1)
        estimated_time_remaining = average_time_per_part * remaining_parts
        
        est_minutes, est_seconds = divmod(estimated_time_remaining, 60)
        print(f"Processed part {i + 1}/{total_parts} in {elapsed_time:.2f} seconds.")
        print(f"Estimated time remaining: {int(est_minutes)} minutes and {int(est_seconds)} seconds.")

    total_time = time.time() - start_time
    total_minutes, total_seconds = divmod(total_time, 60)
    print(f"Total time taken: {int(total_minutes)} minutes and {int(total_seconds)} seconds.")
    
    print(f"Number of entries in input parts array: {len(parts_input)}")
    print(f"Number of entries in output parts array: {len(parts_output)}")
    
    _, ext = os.path.splitext(args.output_file)
    base_filename = os.path.splitext(args.output_file)[0]
    
    if len(parts_output) > 400:
        for i in range(0, len(parts_output), 400):
            part_data = parts_output[i:i + 400]
            part_filename = f"{base_filename}_part{i//400 + 1}{ext}"
            if ext == '.csv':
                export_csv(part_data, part_filename)
            elif ext == '.json':
                export_json(part_data, part_filename)
            print(f"Saved {len(part_data)} entries to {part_filename}")
    else:
        if ext == '.csv':
            export_csv(parts_output, args.output_file)
        elif ext == '.json':
            export_json(parts_output, args.output_file)
        else:
            raise ValueError("Output file must have a .csv or .json extension")

if __name__ == '__main__':
    main()