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
from parse import parse_cart
from export import export_csv
from export import export_xml
from datetime import datetime
from export import export_cart
from request_bricklink import get_color_dict_for_part
from request_bricklink_cart import get_part_and_price_for_lot
from request_lego_store import get_lego_store_result_for_element_id


def setup_logger(log_file, debug):
    """
    Configure and return a logger instance.

    Args:
        log_file (str): The path to the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Stream handler (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def process_cart_file(input_cart_file, log_dir, database_file, skip_purge, debug):
    input_basename = os.path.splitext(os.path.basename(input_cart_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logfile_name = os.path.join(log_dir, f'save_me_money_{input_basename}_{timestamp}.txt')

    logger = setup_logger(logfile_name, debug)

    database = DatabaseManager(database_file, logger)

    # Don't actually process files if purge is requested
    if not skip_purge:
        database.purge_bricklink_store_lots()
        logging.info("Purged all BrickLink store lots")

    # Step 0 - Parse input BrickLink cart file
    cart_lots = parse_cart(input_cart_file)
    logging.info(f"Step 0 complete - Parsed {len(cart_lots)} lots from {input_cart_file}: {cart_lots}")

    # Step 1 - Find out which store and lot IDs need to be requested from BrickLink
    request_cart_lots = {(cart['store_id'], cart['lot_id']) for cart in cart_lots if not database.get_bricklink_cart_entry_by_store_and_lot_id(cart['store_id'], cart['lot_id'])}
    logging.info(f"Step 1 complete - Found {len(request_cart_lots)} new lots to request from BrickLink")
    
    # Step 2 - Make all the requests sequentially and insert the entries into the database
    start_time = time.time()
    database_insertions = 0
    total_lots = len(request_cart_lots)
    for i, (store_id, lot_id) in enumerate(request_cart_lots, 1):
        logging.info(f"Lot {i}/{total_lots}")
        try:
            design_id, color_code, price, type = get_part_and_price_for_lot(store_id, lot_id)
            database.insert_bricklink_cart_entry(store_id, lot_id, price, design_id, color_code, type)
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
    
    # Step 4 - Make all the requests sequentially and insert the entries into the database
    start_time = time.time()
    database_insertions = 0
    total_designs = len(request_design_ids)
    for i, design_id in enumerate(request_design_ids, 1):
        logging.info(f"Design {i}/{total_designs}")
        try:
            data = get_color_dict_for_part(design_id)
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
        element_ids = [element_id for element_id in database.match_bricklink_cart_entries_to_element_ids(cart_lot['store_id'], cart_lot['lot_id'])]
        master_element_ids.update(element_ids)
    request_element_ids = {element_id[0] for element_id in master_element_ids if not database.get_lego_store_entry_by_element_id(element_id[0])}
    logging.info(f"Step 5 complete - Master element IDs (length {len(master_element_ids)}): {master_element_ids}")
    logging.info(f"Step 5 complete - Request element IDs (length {len(request_element_ids)}): {request_element_ids}")
    
    # Step 6 - Make all the requests sequentially and insert the entries into the database
    start_time = time.time()
    database_insertions = 0
    total_elements = len(request_element_ids)
    for i, element_id in enumerate(request_element_ids, 1):
        logging.info(f"Element {i}/{total_elements}")
        try:
            data = get_lego_store_result_for_element_id(element_id)
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
    final_bricklink_partslist = []
    final_lego_lots = []
    for cart_lot in cart_lots:
        # The code `price_compare` appears to be a function or variable name in Python. However,
        # without seeing the actual implementation of the `price_compare` function or variable, it is
        # not possible to determine exactly what it is doing. If you provide more context or the
        # implementation of the `price_compare` function, I can help explain its functionality.
        price_compare = [row for row in database.compare_prices_for_lot(cart_lot['store_id'], cart_lot['lot_id']) if row[1] is not None]
        # print(f"Cart lot with store id {cart_lot['store_id']} and lot id {cart_lot['lot_id']} has price compare of size {len(price_compare)}: {price_compare}")
        price_compare_value = None
        if len(price_compare) == 0:
            final_bricklink_lots.append(cart_lot)
            (_, _, _, design_id, color_code, type) = database.get_bricklink_cart_entry_by_store_and_lot_id(cart_lot['store_id'], cart_lot['lot_id'])
            merged = False
            for part in final_bricklink_partslist:
                if part['design_id'] == design_id and part['color_id'] == color_code:
                    part['quantity'] = str(int(cart_lot['quantity']) + int(part['quantity']))
                    logger.info(f"Adding design ID {design_id} and color code {color_code} and quantity {cart_lot['quantity']} to existing part in BrickLink partslist")
                    merged = True
                    break
            if not merged:
                final_bricklink_partslist.append({
                    'design_id': design_id,
                    'color_id': color_code,
                    'quantity': cart_lot['quantity'],
                    'type': type,
                })
                logger.info(f"Adding design ID {design_id} and color code {color_code} and quantity {cart_lot['quantity']} to new part in BrickLink partslist")
            logger.info(f"Choosing BrickLink price, adding to BrickLink cart: {cart_lot}")
            continue
        elif len(price_compare) == 1:
            price_compare_value = price_compare[0]
            logger.info(f"LEGO option for cart lot with store id {cart_lot['store_id']} and lot id {cart_lot['lot_id']}: {price_compare_value}")
        elif len(price_compare) == 2:
            logger.info(f"Two LEGO options for cart lot with store id {cart_lot['store_id']} and lot id {cart_lot['lot_id']}: {price_compare}")
            if price_compare[0][1] <= price_compare[1][1]:
                price_compare_value = price_compare[0]
            else:
                price_compare_value = price_compare[1]
            logger.info(f"Choosing option: {price_compare_value}")
        else:
            raise AssertionError(f"More than two LEGO options for cart lot with store id {cart_lot['store_id']} and lot id {cart_lot['lot_id']}: {price_compare}")
        if price_compare_value[1] > price_compare_value[2]:
            final_bricklink_lots.append(cart_lot)
            (_, _, _, design_id, color_code, type) = database.get_bricklink_cart_entry_by_store_and_lot_id(cart_lot['store_id'], cart_lot['lot_id'])
            merged = False
            for part in final_bricklink_partslist:
                if part['design_id'] == design_id and part['color_id'] == color_code:
                    part['quantity'] = str(int(cart_lot['quantity']) + int(part['quantity']))
                    logger.info(f"Adding design ID {design_id} and color code {color_code} and quantity {cart_lot['quantity']} to existing part in BrickLink partslist")
                    merged = True
                    break
            if not merged:
                final_bricklink_partslist.append({
                    'design_id': design_id,
                    'color_id': color_code,
                    'quantity': cart_lot['quantity'],
                    'type': type,
                })
                logger.info(f"Adding design ID {design_id} and color code {color_code} and quantity {cart_lot['quantity']} to new part in BrickLink partslist")
            logger.info(f"Choosing BrickLink price, adding to BrickLink cart: {cart_lot}")
        else:
            merged = False
            for lot in final_lego_lots:
                if lot['elementId'] == price_compare_value[0]:
                    lot['quantity'] = str(int(cart_lot['quantity']) + int(lot['quantity']))
                    logger.info(f"Adding element ID {price_compare_value[0]} and quantity {cart_lot['quantity']} to existing part in LEGO list")
                    merged = True
                    break
            if not merged:
                final_lego_lots.append({
                    'elementId': price_compare_value[0],
                    'quantity': cart_lot['quantity'],
                })
                logger.info(f"Adding element ID {price_compare_value[0]} and quantity {cart_lot['quantity']} to new part in LEGO list")
    final_bricklink_lots = sorted(final_bricklink_lots, key=lambda x: (x['store_id'], x['lot_id']))
    logger.info(f"Step 7 complete - Final BrickLink lots (size {len(final_bricklink_lots)}): {final_bricklink_lots}")
    logger.info(f"Step 7 complete - Final LEGO lots (size {len(final_lego_lots)}): {final_lego_lots}")
    
    # Step 8 - Export final BrickLink cart file and LEGO Pick-A-Brick CSV file
    basename = os.path.splitext(input_cart_file)[0]
    bricklink_output_file = f"{basename}_updated_bricklink_cart.cart"
    lego_output_file = f"{basename}_lego_cart.csv"
    bricklink_partslist_file = f"{basename}_bricklink_partslist.xml"
    export_cart(final_bricklink_lots, bricklink_output_file)
    export_csv(final_lego_lots, lego_output_file)
    export_xml(final_bricklink_partslist, bricklink_partslist_file, condition='N')
    logger.info(f"Step 8 complete")


def main():
    """
    Parse command line arguments and run the main program.

    Uses a new BrickLink store lot API to get the price of a lot.
    """
    parser = argparse.ArgumentParser(description='Reduce the cost of a BrickLink cart set by checking parts against LEGO Pick-a-Brick prices.')
    parser.add_argument('input_cart_file', type=str, help='Path to the BrickLink cart file.')
    parser.add_argument('-ld', '--log_dir', type=str, default='logs', help='Path to the directory to save logs.')
    parser.add_argument('-db', '--database_file', type=str, default='part_info.db', help='Path to the SQLite database file.')
    parser.add_argument('--skip-purge', action='store_true', help='Skip purging the BrickLink store lots.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    args = parser.parse_args()

    process_cart_file(args.input_cart_file, args.log_dir, args.database_file, args.skip_purge, args.debug)


if __name__ == '__main__':
    main()
