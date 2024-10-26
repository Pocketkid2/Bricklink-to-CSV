"""
Convert.

This module processes XML files and exports the data to CSV or JSON files.
It also sets up logging and handles database operations.
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


if __name__ == '__main__':
    main()
