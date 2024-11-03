"""
Convert - The main flow.

This is what you came here for. The main program that converts BrickLink XMLs
into CSV/JSON that can be uploaded to LEGO's Pick-a-Brick store. It is a
complex and lengthy process, because it involves web scraping to map the
bricklink codes to the lego codes, and also tries to handle issues that
inevitably arise, particularly with larger builds.
"""

import os
import sys
import math
import logging
import argparse
import time
from database import *
import concurrent.futures
from parse import parse_xml
from export import export_csv, export_json, export_xml
from request_bricklink import get_color_dict_for_part
from request_lego_store import get_lego_store_result_for_element_id


def split_array_into_equal_chunks(array, num_chunks):
    """
    Break an array into num_chunks roughly equal pieces.

    Args:
        array (list): The array to be divided.
        num_chunks (int): The number of chunks to divide the array into.

    Returns:
        list of lists: A list containing the chunks.
    """
    avg = len(array) / float(num_chunks)
    chunks = [array[int(round(avg * i)): int(round(avg * (i + 1)))] for i in range(num_chunks)]
    return chunks


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
    parser.add_argument('input_xml_file', help='Path to the input XML file')
    parser.add_argument('-l', '--log_file', default='log.txt', help='Path to the log file')
    parser.add_argument('-db', '--database_file', default='part_info.db', help='Path to the SQLite database file')
    parser.add_argument('-pb', '--purge_bricklink', action='store_true', help='Purge the BrickLink table in the database before processing the XML')
    parser.add_argument('-pl', '--purge_lego_store', action='store_true', help='Purge the LEGO Pick-a-Brick table in the database before processing the XML')
    parser.add_argument('-new', '--bricklink_new', action='store_true', help='Set part condition to NEW for unavailable items exported back to BrickLink XML')
    parser.add_argument('-used', '--bricklink_used', action='store_true', help='Set part condition to USED for unavailable items exported back to BrickLink XML')
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
    bricklink_xml_partslist = parse_xml(args.input_xml_file)
    logging.info(f"Step 0 complete - bricklink XML partslist (length {len(bricklink_xml_partslist)}): {bricklink_xml_partslist}")

    # Step 1 - round up all design IDs
    unique_design_ids = {part['design_id'] for part in bricklink_xml_partslist}
    logging.info(f"Step 1 complete - unique design IDs (length {len(unique_design_ids)}): {unique_design_ids}")

    # Step 2 - Find out which design IDs are NOT in the bricklink database table
    request_design_ids = {design_id for design_id in unique_design_ids if not database.get_bricklink_entry_by_design_id(design_id)}
    logging.info(f"Step 2 complete - request design IDs (length {len(request_design_ids)}): {request_design_ids}")

    # Step 3 - Make the requests to bricklink for all the missing design IDs
    start_time = time.time()
    database_insertions = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_design_id = {executor.submit(get_color_dict_for_part, design_id): design_id for design_id in request_design_ids}
        for future in concurrent.futures.as_completed(future_to_design_id):
            design_id = future_to_design_id[future]
            try:
                data = future.result()
                for color_code, element_id_list in data.items():
                    for element_id in element_id_list:
                        database.insert_bricklink_entry(element_id, design_id, color_code)
                        database_insertions += 1
            except Exception as exc:
                logging.error(f"Step 3 - Design ID {design_id} generated an exception: {exc}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    logging.info(f"Step 3 complete - database insertions: {database_insertions}, time taken: {minutes} minutes and {seconds} seconds")

    # Step 4 - Create a master list of all potential element IDs
    master_element_ids = set()
    for part in bricklink_xml_partslist:
        element_ids = [element_id for (element_id, _, _) in database.get_bricklink_entries_by_design_id_and_color_code(part['design_id'], part['color_id'])]
        master_element_ids.update(element_ids)
    logging.info(f"Step 4 complete - master element IDs (length {len(master_element_ids)}): {master_element_ids}")

    # Step 5 - Find out which element IDs are not in the lego pick-a-brick database table
    request_element_ids = {element_id for element_id in master_element_ids if not database.get_lego_store_entry_by_element_id(element_id)}
    logging.info(f"Step 5 complete - request element IDs (length {len(request_element_ids)}): {request_element_ids}")

    # Step 6 - Make the requests to lego pick-a-brick for all the missing element IDs
    start_time = time.time()
    database_insertions = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_element_id = {executor.submit(get_lego_store_result_for_element_id, element_id): element_id for element_id in request_element_ids}
        for future in concurrent.futures.as_completed(future_to_element_id):
            element_id = future_to_element_id[future]
            try:
                data = future.result()
                if data is None:
                    database.insert_lego_store_entry(element_id, lego_sells=False, bestseller=None, price=None, max_order_quantity=None)
                    database_insertions += 1
                else:
                    if data['deliveryChannel'] not in ['pab', 'bap']:
                        raise ValueError(f"Invalid delivery channel: {data['deliveryChannel']}")
                    database.insert_lego_store_entry(element_id,
                                                     lego_sells=True,
                                                     bestseller=(data['deliveryChannel'] == 'pab'),
                                                     price=data['price']['centAmount'],
                                                     max_order_quantity=data['maxOrderQuantity'])
                    database_insertions += 1
            except Exception as exc:
                logging.error(f"Step 6 - Element ID {element_id} generated an exception: {exc}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    logging.info(f"Step 6 complete - database insertions: {database_insertions}, time taken: {minutes} minutes and {seconds} seconds")

    # Step 7 - Resolve all potential issues with the data

    not_available_final_list = []
    not_available_total_count = 0
    bucket_one_available = []
    bucket_two_available = []

    # Step 7.1 - For each part in the original list, find out how many elements it has that LEGO sells
    LEGO_SELLS_COLUMN = 4
    for part in bricklink_xml_partslist:
        available_elements = 0
        element_results = database.match_bricklink_entries_to_lego_store_entries(part['design_id'], part['color_id'])

        for element_result in element_results:
            if element_result[LEGO_SELLS_COLUMN]:
                available_elements += 1

        if available_elements == 0:
            not_available_final_list.append(part)
            not_available_total_count += int(part['quantity'])
        elif available_elements == 1:
            bucket_one_available.append(part)
        elif available_elements == 2:
            bucket_two_available.append(part)
        else:
            logging.error(f"Part {part} has {available_elements} available elements from the store")

    logging.info(f"Step 7.1 complete - bucket not available (length {len(not_available_final_list)}): {not_available_final_list}")
    logging.info(f"Step 7.1 complete - bucket one available (length {len(bucket_one_available)}): {bucket_one_available}")
    logging.info(f"Step 7.1 complete - bucket two available (length {len(bucket_two_available)}): {bucket_two_available}")

    # Step 7.2 - Find out how many "one available" options are bestseller vs not
    BESTSELLER_COLUMN = 5

    bestseller_final_list = []
    bestseller_total_count = 0

    non_bestseller_final_list = []
    non_bestseller_total_count = 0

    for part in bucket_one_available:
        element_results = database.match_bricklink_entries_to_lego_store_entries(part['design_id'], part['color_id'])

        for element_result in element_results:
            if element_result[LEGO_SELLS_COLUMN]:
                if element_result[BESTSELLER_COLUMN]:
                    bestseller_final_list.append({'elementId': element_result[0], 'quantity': part['quantity']})
                    bestseller_total_count += int(part['quantity'])
                else:
                    non_bestseller_final_list.append({'elementId': element_result[0], 'quantity': part['quantity']})
                    non_bestseller_total_count += int(part['quantity'])

    logging.info(f"Step 7.2 complete - In the 'one available' bucket, bestseller has {len(bestseller_final_list)} lots \
                   and {bestseller_total_count} total parts, non-bestseller has {len(non_bestseller_final_list)} lots \
                   and {non_bestseller_total_count} total parts")

    # Step 7.3 - Compare prices and max order quantity for each of the "two available" parts
    PRICE_COLUMN = 6
    MAX_ORDER_QUANTITY_COLUMN = 7

    for part in bucket_two_available:
        element_results = database.match_bricklink_entries_to_lego_store_entries(part['design_id'], part['color_id'])

        options = []

        for element_result in element_results:
            if element_result[LEGO_SELLS_COLUMN]:
                options.append({
                    'elementId': element_result[0],
                    'quantity': part['quantity'],
                    'price': element_result[PRICE_COLUMN],
                    'maxOrderQuantity': element_result[MAX_ORDER_QUANTITY_COLUMN],
                    'bestseller': element_result[BESTSELLER_COLUMN]
                })
                logger.info(f"Comparing part {part} with element ID {element_result[0]} - Max Order Quantity: {element_result[MAX_ORDER_QUANTITY_COLUMN]}, \
                              BestSeller = {element_result[BESTSELLER_COLUMN]}, Price: {element_result[PRICE_COLUMN]} cents")

        print("You must choose one of the following options:")
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        option = None
        if options[0]['price'] != options[1]['price']:
            option = options[0] if options[0]['price'] < options[1]['price'] else options[1]
        while option is None:
            try:
                submitted = int(input("Which option would you like to choose? "))
                if submitted < 1 or submitted > len(options):
                    print(f"Invalid option: {submitted}")
                else:
                    option = options[submitted - 1]
            except ValueError as exc:
                print(f"Invalid option: {exc}")
                option = None

        if option['bestseller']:
            bestseller_final_list.append({'elementId': option['elementId'], 'quantity': option['quantity']})
            bestseller_total_count += int(part['quantity'])
        else:
            non_bestseller_final_list.append({'elementId': option['elementId'], 'quantity': option['quantity']})
            non_bestseller_total_count += int(part['quantity'])

        logging.info(f"User chose option {option}")

    logger.info(f"Step 7.3 complete - Price and max order quantity comparison complete; bestseller now has {len(bestseller_final_list)} lots \
                  and {bestseller_total_count} total parts, non-bestseller has {len(non_bestseller_final_list)} lots \
                  and {non_bestseller_total_count} total parts")

    # Step 8 - export the data to the output file

    # Step 8.1 - export the not available parts
    not_available_filename = os.path.splitext(args.input_xml_file) + '_not_available.xml'
    condition = None
    if args.bricklink_new:
        condition = 'N'
    elif args.bricklink_used:
        condition = 'U'
    else:
        condition = 'X'
    export_xml(not_available_final_list, not_available_filename, condition)

    # Step 8.2 - Break lists into sub-lists to keep each under 200 lots
    bestseller_chunks = []
    num_bestseller_chunks = 0
    if (len(bestseller_final_list) / 200) > 1:
        num_bestseller_chunks = math.ceil(len(bestseller_final_list) / 200)
        bestseller_chunks = split_array_into_equal_chunks(bestseller_final_list, num_bestseller_chunks)
    else:
        num_bestseller_chunks = 1
        bestseller_chunks = [bestseller_final_list]

    non_bestseller_chunks = []
    num_non_bestseller_chunks = 0
    if (len(non_bestseller_final_list) / 200) > 1:
        num_non_bestseller_chunks = math.ceil(len(non_bestseller_final_list) / 200)
        non_bestseller_chunks = split_array_into_equal_chunks(non_bestseller_final_list, num_non_bestseller_chunks)
    else:
        num_non_bestseller_chunks = 1
        non_bestseller_chunks = [non_bestseller_final_list]

    logger.info(f"Step 8.2 complete - bestseller list will be written in {num_bestseller_chunks} chunks, non-bestseller list \
                  will be written in {num_non_bestseller_chunks} chunks")

    # Step 8.3 - export all parts to CSV or JSON, breaking up the individual lists to be under 200 lots per delivery
    for export_function in [export_csv, export_json]:
        file_extension = export_function.__name__.split('_')[1]
        for i in range(0, max(num_bestseller_chunks, num_non_bestseller_chunks)):
            output_filename = os.path.splitext(args.input_xml_file)[0] + f'_order{i+1}.' + file_extension
            bestseller_chunk = []
            non_bestseller_chunk = []
            if i < num_bestseller_chunks:
                bestseller_chunk = bestseller_chunks[i]
            if i < num_non_bestseller_chunks:
                non_bestseller_chunk = non_bestseller_chunks[i]
            export_function(bestseller_chunk + non_bestseller_chunk, output_filename)
            logger.info(f"Wrote {len(bestseller_chunk)} + {len(non_bestseller_chunk)} = {len(bestseller_chunk + non_bestseller_chunk)} \
                          entries to {output_filename}")

    # Step 9 - close the database
    database.close()


if __name__ == '__main__':
    main()
