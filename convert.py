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

    bricklink_parts = parse_xml(args.input_xml)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        lego_parts = list(executor.map(process_bricklink_part_to_lego_part, bricklink_parts))
        print(f"Processed {len(lego_parts)} parts")
        logging.info(f"Processed {len(lego_parts)} parts")
        for part_list in lego_parts:
            if part_list is None:
                print("Could not find color info for part")
            elif not part_list:
                print("No available LEGO parts found for this part/color combination")
            else:
                print(f"Found {len(part_list)} LEGO parts for this part/color combination")
                for part in part_list:
                    print(part)







    
    # _, ext = os.path.splitext(args.output_file)
    # base_filename = os.path.splitext(args.output_file)[0]
    
    # if len(parts_output) > 400:
    #     for i in range(0, len(parts_output), 400):
    #         part_data = parts_output[i:i + 400]
    #         part_filename = f"{base_filename}_part{i//400 + 1}{ext}"
    #         if ext == '.csv':
    #             export_csv(part_data, part_filename)
    #         elif ext == '.json':
    #             export_json(part_data, part_filename)
    #         print(f"Saved {len(part_data)} entries to {part_filename}")
    # else:
    #     if ext == '.csv':
    #         export_csv(parts_output, args.output_file)
    #     elif ext == '.json':
    #         export_json(parts_output, args.output_file)
    #     else:
    #         raise ValueError("Output file must have a .csv or .json extension")

if __name__ == '__main__':
    main()