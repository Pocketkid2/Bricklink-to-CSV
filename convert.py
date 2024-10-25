import logging
import argparse
import concurrent.futures
from colors import colors_by_id
from grab_color_info import get_color_dict_for_part


def process_bricklink_part_to_lego_part(bricklink_part):
    design_id = bricklink_part['design_id']
    color_id = bricklink_part['color_id']
    quantity = bricklink_part['quantity']

    print(f"Processing part {design_id} in color {color_id} with quantity {quantity}")
    logging.info(f"Processing part {design_id} in color {color_id} with quantity {quantity}")

    color_dict = get_color_dict_for_part(design_id)
    if not color_dict:
        print(f"Could not find color info for part {design_id} (input color {color_id}, input quantity {quantity})")
        logging.warning(f"Could not find color info for part {design_id} (input color {color_id}, input quantity {quantity})")
        return None
    
    print(f"Found {len(color_dict)} colors for part {design_id}")
    logging.info(f"Found {len(color_dict)} colors for part {design_id}")

    lego_parts = []
    for color_code, element_ids in color_dict.items():
        for element_id in element_ids:
            if color_code == color_id:
                # TODO - Apply LEGO.com API to filter this and add another column for bestseller/not and price
                lego_part = {
                    'elementId': element_id,
                    'quantity': quantity
                }
                lego_parts.append(lego_part)

    print(f"Found {len(lego_parts)} LEGO parts for part {design_id} in color {color_id}")
    logging.info(f"Found {len(lego_parts)} LEGO parts for part {design_id} in color {color_id}")

    return lego_parts


def main():
    parser = argparse.ArgumentParser(description='Process XML and export to CSV or JSON.')
    parser.add_argument('input_xml', help='Path to the input XML file')
    parser.add_argument('output_file', help='Path to the output file')
    parser.add_argument('log_file', help='Path to the log file')
    args = parser.parse_args()

    logging.basicConfig(filename=args.log_file, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')


if __name__ == '__main__':
    main()