import os
import sys
import logging
import argparse
from parse import parse_xml
from export import export_xml

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

def merge_parts(partslist_2d, logger):
    """
    Merge parts by summing quantities for duplicate design_id and color_id combinations.

    Args:
        parts_list (list of list of dict): List of parts lists to be merged.

    Returns:
        list of dict: Merged parts list.
    """
    merged_parts = {}
    for partslist_1d in partslist_2d:
        for part in partslist_1d:
            key = (part['design_id'], part['color_id'])
            if key in merged_parts:
                logger.info(f"Combining {part['quantity']:3} with {merged_parts[key]['quantity']:3} for {key}")
                merged_parts[key]['quantity'] = str(int(merged_parts[key]['quantity']) + int(part['quantity']))
            else:
                merged_parts[key] = part.copy()
    return list(merged_parts.values())

def main():
    """
    Parse command-line arguments, set up logging, and merge XML files.
    """
    parser = argparse.ArgumentParser(description='Merge XML files and export to a single XML file.')
    parser.add_argument('output_xml_file', help='Path to the output XML file')
    parser.add_argument('input_xml_files', nargs='+', help='Paths to the input XML files')
    parser.add_argument('-l', '--log_file', default='log.txt', help='Path to the log file')
    parser.add_argument('-new', '--bricklink_new', action='store_true', help='Set part condition to NEW for items exported back to BrickLink XML')
    parser.add_argument('-used', '--bricklink_used', action='store_true', help='Set part condition to USED for items exported back to BrickLink XML')
    args = parser.parse_args()

    if not args.output_xml_file.endswith('.xml'):
        logging.error(f"Invalid output file type: {args.output_xml_file}")
        return

    for input_file in args.input_xml_files:
        if not input_file.endswith('.xml'):
            logging.error(f"Invalid input file type: {input_file}")
            return

    logger = setup_logger(args.log_file)

    all_parts = []
    for input_file in args.input_xml_files:
        parts = parse_xml(input_file)
        all_parts.append(parts)
        logger.info(f"Parsed {len(parts)} entries from {input_file}")

    merged_parts = merge_parts(all_parts, logger)
    logger.info(f"Merged parts list contains {len(merged_parts)} unique entries")

    condition = None
    if args.bricklink_new:
        condition = 'N'
    elif args.bricklink_used:
        condition = 'U'
    else:
        condition = 'X'

    export_xml(merged_parts, args.output_xml_file, condition)
    logger.info(f"Exported merged parts list to {args.output_xml_file}")

if __name__ == '__main__':
    main()