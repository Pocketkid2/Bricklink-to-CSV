"""
Save Me Money.

Reduce the cost of a BrickLink cart set by checking parts against LEGO Pick-a-Brick prices.
"""

import os
import logging
import datetime
import argparse
from database import *
from parse import parse_cart


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
    logfile_name = os.path.join(args.log_dir, f'save_me_money_{input_basename}_{timestamp}.log')

    logger = setup_logger(logfile_name)

    database = DatabaseManager(args.database_file, logger)

    # Don't actually process files if purge is requested
    if args.purge_cart_table:
        database.purge_bricklink_store_lots()
        return

    # Step 0 - Parse input BrickLink cart file
    carts = parse_cart(args.input_cart_file)
    logging.info(f"Step 0 complete - Parsed {len(carts)} lots from {args.input_cart_file}")

    # Step 1 - Find out which store and lot IDs need to be requested from BrickLink
    # Step 2 - Make all the requests in parallel and insert the entries into the database
    # Step 3 - Find out which design and color IDs need to be requested from BrickLink (API exists)
    # Step 4 - Make all the requests in parallel and insert the entries into the databse
    # Step 5 - Find out which element IDs need to be requested from LEGO (API exists)
    # Step 6 - Make all the requests in parallel and insert the entries into the database
    # Step 7 - Do the triple join, and find all rows that have a bricklink store entry and at least one lego store entry
    # Step 8 - Look through those rows and find the lowest price - sometimes LEGO will have two options of same price, handle that
    # Step 9 - Export LEGO Pick-A-Brick CSV and JSON for those extracted cheaper parts
    # Step 10 - Export BrickLink cart with Pick-A-Brick parts removed
    print(carts)


if __name__ == '__main__':
    main()
