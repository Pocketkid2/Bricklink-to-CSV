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
    parser.add_argument('log_file', default='log.txt', help='Path to the log file')
    parser.add_argument('database_file', default='part_info.db', help='Path to the SQLite database file')
    parser.add_argument('-pb', '--purge_bricklink', action='store_true', help='Purge the BrickLink table in the database before processing the XML')
    parser.add_argument('-pl', '--purge_lego_pab', action='store_true', help='Purge the LEGO Pick-a-Brick table in the database before processing the XML')
    args = parser.parse_args()

    logger = setup_logger(args.log_file)
    
    database = DatabaseManager(args.database_file, logger)
    
    # Don't actually convert if purge is requested
    if args.purge_bricklink:
        database.purge_bricklink_table()
        return
    if args.purge_lego_pab:
        database.purge_lego_pab_table()
        return
    
    # Step 1 - round up all design IDs
    
    # Step 2 - Find out which design IDs are NOT in the bricklink database table
    
    # Step 3 - Make the requests to bricklink for all the missing design IDs
    
    # Step 4 - Create a master list of all potential element IDs
    
    # Step 5 - Find out which element IDs are not in the leg pick-a-brick database table
    
    # Step 6 - Make the requests to lego pick-a-brick for all the missing element IDs
    
    # Step 7 - Resolve all potential issues with the data
    
    # Step 8 - export the data to the output file

if __name__ == '__main__':
    main()
