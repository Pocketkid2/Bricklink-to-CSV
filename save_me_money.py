"""
Save Me Money.

Reduce the cost of a BrickLink cart set by checking parts against LEGO Pick-a-Brick prices.
"""

import os
import sys
import time
import logging
from datetime import datetime
import argparse
import concurrent.futures
from database import *
from parse import parse_cart
from request_bricklink import get_color_dict_for_part
from request_bricklink_cart import get_part_and_price_for_lot


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
    Parse command line arguments and run the main program.

    Uses a new BrickLink store lot API to get the price of a lot.
    """
    parser = argparse.ArgumentParser(description='Reduce the cost of a BrickLink cart set by checking parts against LEGO Pick-a-Brick prices.')
    parser.add_argument('input_cart_file', type=str, help='Path to the BrickLink cart file.')
    parser.add_argument('-ld', '--log_dir', type=str, default='logs', help='Path to the directory to save logs.')
    parser.add_argument('-db', '--database_file', type=str, default='part_info.db', help='Path to the SQLite database file.')
    parser.add_argument('-pc', '--purge_cart_table', action='store_true', help='Purge the table of BrickLink lots (from cart) in the database.')
    args = parser.parse_args()

    input_basename = os.path.splitext(os.path.basename(args.input_cart_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logfile_name = os.path.join(args.log_dir, f'save_me_money_{input_basename}_{timestamp}.txt')

    logger = setup_logger(logfile_name)

    database = DatabaseManager(args.database_file, logger)

    # Don't actually process files if purge is requested
    if args.purge_cart_table:
        database.purge_bricklink_store_lots()
        return

    # Step 0 - Parse input BrickLink cart file
    cart_lots = parse_cart(args.input_cart_file)
    logging.info(f"Step 0 complete - Parsed {len(cart_lots)} lots from {args.input_cart_file}")

    # Step 1 - Find out which store and lot IDs need to be requested from BrickLink
    request_cart_lots = {(cart['store_id'], cart['lot_id']) for cart in cart_lots if not database.get_bricklink_cart_entry_by_store_and_lot_id(cart['store_id'], cart['lot_id'])}
    logging.info(f"Step 1 complete - Found {len(request_cart_lots)} new lots to request from BrickLink")
    
    # Step 2 - Make all the requests in parallel and insert the entries into the database
    start_time = time.time()
    database_insertions = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_design_id = {executor.submit(get_part_and_price_for_lot, store_id, lot_id): (store_id, lot_id) for store_id, lot_id in request_cart_lots}
        for future in concurrent.futures.as_completed(future_to_design_id):
            store_id, lot_id = future_to_design_id[future]
            try:
                design_id, color_code, price = future.result()
                database.insert_bricklink_cart_entry(store_id, lot_id, price, design_id, color_code)
                database_insertions += 1
            except Exception as e:
                logging.error(f"Exception raised for {store_id}, {lot_id}: {e}")
    database.commit_changes()
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    logging.info(f"Step 2 complete - Inserted {database_insertions} new lots in {minutes} minutes and {seconds} seconds")

    # Step 3 - Find out which design and color IDs need to be requested from BrickLink (API exists)
    request_design_ids = set()
    for cart_lot in cart_lots:
        bricklink_data = database.get_bricklink_cart_entry_by_store_and_lot_id(cart_lot['store_id'], cart_lot['lot_id'])
        if bricklink_data:
            design_id = bricklink_data[3]
            color_code = bricklink_data[4]
            if not database.get_bricklink_entry_by_design_id(design_id):
                request_design_ids.add(design_id)
    logging.info(f"Step 3 complete - request design IDs (length {len(request_design_ids)}): {request_design_ids}")
    
    # Step 4 - Make all the requests in parallel and insert the entries into the database
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
    database.commit_changes()
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    logging.info(f"Step 4 complete - Inserted {database_insertions} new design IDs in {minutes} minutes and {seconds} seconds")
    
    # Step 5 - Find out which element IDs need to be requested from LEGO (API exists)
    # Step 6 - Make all the requests in parallel and insert the entries into the database
    # Step 7 - Do the triple join, and find all rows that have a bricklink store entry and at least one lego store entry
    # Step 8 - Look through those rows and find the lowest price - sometimes LEGO will have two options of same price, handle that
    # Step 9 - Export LEGO Pick-A-Brick CSV and JSON for those extracted cheaper parts
    # Step 10 - Export BrickLink cart with Pick-A-Brick parts removed


if __name__ == '__main__':
    main()
