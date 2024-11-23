"""
Save Me Money.

Reduce the cost of a BrickLink cart set by checking parts against LEGO Pick-a-Brick prices.
"""

import os
import sys
import time
import logging
import argparse
from database import *
import concurrent.futures
from parse import parse_cart
from export import export_csv
from datetime import datetime
from export import export_cart
from request_bricklink import get_color_dict_for_part
from request_bricklink_cart import get_part_and_price_for_lot
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
    logging.info(f"Step 0 complete - Parsed {len(cart_lots)} lots from {args.input_cart_file}: {cart_lots}")

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
    master_element_ids = set()
    for cart_lot in cart_lots:
        element_ids = [element_id for element_id in database.match_bricklink_entries_to_bricklink_cart_entries(cart_lot['store_id'], cart_lot['lot_id'])]
        master_element_ids.update(element_ids)
    request_element_ids = {element_id[0] for element_id in master_element_ids if not database.get_lego_store_entry_by_element_id(element_id[0])}
    logging.info(f"Step 5 complete - Master element IDs (length {len(master_element_ids)}): {master_element_ids}")
    logging.info(f"Step 5 complete - Request element IDs (length {len(request_element_ids)}): {request_element_ids}")
    
    # Step 6 - Make all the requests in parallel and insert the entries into the database
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
                                                     price=data['price']['formattedAmount'],
                                                     max_order_quantity=data['maxOrderQuantity'])
                    database_insertions += 1
            except Exception as exc:
                logging.error(f"Step 6 - Element ID {element_id} generated an exception: {exc}")
    database.commit_changes()
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    logging.info(f"Step 6 complete - database insertions: {database_insertions}, time taken: {minutes} minutes and {seconds} seconds")
    
    # Step 7 - Do the triple join, and find all rows that have a bricklink store entry and at least one lego store entry
    final_bricklink_lots = []
    final_lego_lots = []
    for cart_lot in cart_lots:
        price_compare = [row for row in database.compare_prices_for_lot(cart_lot['store_id'], cart_lot['lot_id']) if row[1] is not None]
        # print(f"Cart lot with store id {cart_lot['store_id']} and lot id {cart_lot['lot_id']} has price compare of size {len(price_compare)}: {price_compare}")
        price_compare_value = None
        if len(price_compare) == 1:
            price_compare_value = price_compare[0]
            logger.info(f"Price compare value: {price_compare_value}")
        elif len(price_compare) == 2:
            print(f"Cart lot with store id {cart_lot['store_id']} and lot id {cart_lot['lot_id']} has two price compare values:")
            for index, row in enumerate(price_compare):
                print(index, row)
            while True:
                try:
                    choice = int(input("Choose one (0 or 1): "))
                    if choice in [0, 1]:
                        break
                except ValueError:
                    pass
            price_compare_value = price_compare[choice]
        else:
            continue
        if price_compare_value[1] > price_compare_value[2]:
            final_bricklink_lots.append(cart_lot)
            logger.info(f"Choosing BrickLink price, adding to BrickLink cart: {cart_lot}")
        else:
            lego_lot = {
                'elementId': price_compare_value[0],
                'quantity': cart_lot['quantity'],
            }
            final_lego_lots.append(lego_lot)
            logger.info(f"Choosing LEGO price, adding to LEGO cart: {lego_lot}")
    final_bricklink_lots = sorted(final_bricklink_lots, key=lambda x: (x['store_id'], x['lot_id']))
    logger.info(f"Step 7 complete - Final BrickLink lots (size {len(final_bricklink_lots)}): {final_bricklink_lots}")
    logger.info(f"Step 7 complete - Final LEGO lots (size {len(final_lego_lots)}): {final_lego_lots}")
    
    # Step 8 - Export final BrickLink cart file and LEGO Pick-A-Brick CSV file
    basename = os.path.splitext(args.input_cart_file)[0]
    bricklink_output_file = f"{basename}_updated_bricklink_cart.cart"
    lego_output_file = f"{basename}_lego_cart.csv"
    export_cart(final_bricklink_lots, bricklink_output_file)
    export_csv(final_lego_lots, lego_output_file)
    logger.info(f"Step 8 complete - Exported {len(final_bricklink_lots)} entries to {bricklink_output_file}")
    logger.info(f"Step 8 complete - Exported {len(final_lego_lots)} entries to {lego_output_file}")


if __name__ == '__main__':
    main()
