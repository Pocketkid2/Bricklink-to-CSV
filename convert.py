"""
Convert - The main flow.

This is what you came here for. The main program that converts BrickLink XMLs
into CSV/JSON that can be uploaded to LEGO's Pick-a-Brick store. It is a
complex and lengthy process, because it involves web scraping to map the
bricklink codes to the lego codes, and also tries to handle issues that
inevitably arise, particularly with larger builds.
"""

import sys
import logging
import argparse
from database import *
import concurrent.futures
from parse import parse_xml
from request_bricklink import get_color_dict_for_part
from request_lego_store import get_lego_store_result_for_element_id


def setup_logger(log_file):
    """
    Configure and return a logger instance.

    Args:
        log_file (str): The path to the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Stream handler (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def main():
    """
    Parse command-line arguments, set up logging, and process the XML file.

    This function handles the main workflow of the script, including parsing
    command-line arguments, setting up logging, and processing the input XML
    file to export data to CSV or JSON.
    """
    parser = argparse.ArgumentParser(description='Process XML and export to CSV or JSON.')
    parser.add_argument('input_xml', help='Path to the input XML file')
    parser.add_argument('output_file', help='Path to the output file')
    parser.add_argument('-l', '--log_file', default='log.txt', help='Path to the log file')
    parser.add_argument('-db', '--database_file', default='part_info.db', help='Path to the SQLite database file')
    parser.add_argument('-pb', '--purge_bricklink', action='store_true', help='Purge the BrickLink table in the database before processing the XML')
    parser.add_argument('-pl', '--purge_lego_store', action='store_true', help='Purge the LEGO Pick-a-Brick table in the database before processing the XML')
    args = parser.parse_args()

    logger = setup_logger(args.log_file)
    
    database = DatabaseManager(args.database_file, logger)
    
    # Don't actually convert if purge is requested
    if args.purge_bricklink:
        database.purge_bricklink_table()
        return
    if args.purge_lego_store:
        database.purge_lego_store_table()
        return
    
    # Step 0 - Parse input XML file
    bricklink_xml_partslist = parse_xml(args.input_xml)
    print(f"Step 0 - bricklink xml partslist: {bricklink_xml_partslist}")
    
    # Step 1 - round up all design IDs
    unique_design_ids = {part['design_id'] for part in bricklink_xml_partslist}
    print(f"Step 1 - unique design IDs: {unique_design_ids}")
    
    # Step 2 - Find out which design IDs are NOT in the bricklink database table
    request_design_ids = {design_id for design_id in unique_design_ids if not database.get_bricklink_entry_by_design_id(design_id)}
    print(f"Step 2 - request design IDs: {request_design_ids}")
    
    # Step 3 - Make the requests to bricklink for all the missing design IDs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_design_id = {executor.submit(get_color_dict_for_part, design_id): design_id for design_id in request_design_ids}
        for future in concurrent.futures.as_completed(future_to_design_id):
            design_id = future_to_design_id[future]
            try:
                data = future.result()
                for color_code, element_id_list in data.items():
                    for element_id in element_id_list:
                        database.insert_bricklink_entry(element_id, design_id, color_code)
            except Exception as exc:
                print(f"Step 3 - Design ID {design_id} generated an exception: {exc}")
    
    # Step 4 - Create a master list of all potential element IDs
    master_element_ids = set()
    for part in bricklink_xml_partslist:
        element_ids = [element_id for (element_id, _, _) in database.get_bricklink_entries_by_design_id_and_color_code(part['design_id'], part['color_id'])]
        master_element_ids.update(element_ids)
        print(f"Step 4 - element IDs for design ID {part['design_id']} and color code {part['color_id']}: {element_ids}")
    
    # Step 5 - Find out which element IDs are not in the lego pick-a-brick database table
    request_element_ids = {element_id for element_id in master_element_ids if not database.get_lego_store_entry_by_element_id(element_id)}
    print(f"Step 5 - request element IDs: {request_element_ids}")
    
    # Step 6 - Make the requests to lego pick-a-brick for all the missing element IDs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_element_id = {executor.submit(get_lego_store_result_for_element_id, element_id): element_id for element_id in request_element_ids}
        for future in concurrent.futures.as_completed(future_to_element_id):
            element_id = future_to_element_id[future]
            try:
                data = future.result()
                if data is None:
                    database.insert_lego_store_entry(element_id, lego_sells=False, bestseller=None, price=None, max_order_quantity=None)
                else:
                    if data['deliveryChannel'] not in ['pab', 'bap']:
                        raise ValueError(f"Invalid delivery channel: {data['deliveryChannel']}")
                    database.insert_lego_store_entry(element_id, lego_sells=True, bestseller=(data['deliveryChannel'] == 'pab'), price=data['price']['centAmount'], max_order_quantity=data['maxOrderQuantity'])
                print(f"Step 6 - Element ID {element_id} data: {data}")
            except Exception as exc:
                print(f"Step 6 - Element ID {element_id} generated an exception: {exc}")
    
    # Step 7 - Resolve all potential issues with the data
    #   case 1 = part doesn't exist
    #   case 2 = part exists, one version
    #   case 3 = part exists, multiple versions (likely 1 each for bestseller & 1 not)
    # DECIDE - What do about parts in each of these cases?
    # DECIDE - how to split up if reached maximum part count?
    # FACT: 200 max lots for bestseller cart, $7 service fee for orders under $14,shipping $11.95
    # FACT: 200 max lots for non-bestseller cart, $7 service fee for orders under $14, shipping $11.95
    # FACT: If shipping both bestseller and non-bestseller, $18.95 shipping for both
    # FACT: max quantity of a single item is 999
    # FACT: If you have a large enough order, free shipping
    bucket_zero = []
    bucket_one = []
    bucket_two = []
    for index, part in enumerate(bricklink_xml_partslist):
        element_ids = [element_id for (element_id, _, _) in database.get_bricklink_entries_by_design_id_and_color_code(part['design_id'], part['color_id'])]
        for element_id in element_ids:
            lego_store_entry = database.get_lego_store_entry_by_element_id(element_id)
            if lego_store_entry is None:
                print(f"Step 7 - Element ID {element_id} does not exist in the LEGO Pick-a-Brick database")
            else:
                print(f"Step 7 - Element ID {element_id} data: {lego_store_entry}")
    
    # Step 8 - export the data to the output file
    
    # Step 9 - close the database
    database.close()

if __name__ == '__main__':
    main()
