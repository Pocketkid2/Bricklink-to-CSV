"""Bricklink Request.

This module contains the API needed for making web requests to BrickLink.com
and obtaining a color dictionary for a given part number (design ID).
"""

import sys
import logging
import requests
from bs4 import BeautifulSoup
from colors import colors_by_name


def get_color_dict_for_part(design_id):
    """
    Get a color dictionary for a given part number (design ID).

    Args:
        design_id (int): The part number (design ID).

    Returns:
        dict: A dictionary mapping color IDs to lists of element IDs.
    """
    webpage_content = get_webpage_for_part(design_id)
    color_table = find_color_table_in_page(webpage_content)
    if not color_table:
        logging.error(f"Could not find color table for design ID: {design_id}")
        return
    color_dict = convert_table_to_dict(color_table)
    return color_dict


def get_webpage_for_part(design_id):
    """
    Get the webpage content for a given part number (design ID).

    Args:
        design_id (int): The part number (design ID).

    Raises:
        http_err: An HTTP error occurred.
        err: An error occurred.

    Returns:
        bytes: The content of the webpage.
    """
    try:
        url = f"https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo={design_id}"
        logging.info(f"Fetching {url}...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"})
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.content
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Error code: {response.status_code}")
        logging.error(f"Error data: {response.text}")
        raise http_err
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        raise err


def find_color_table_in_page(page_content):
    """
    Find the color table in the given page content.

    Args:
        page_content (bytes): The content of the webpage.

    Returns:
        bs4.element.Tag: The color table element.
    """
    soup = BeautifulSoup(page_content, 'lxml')
    tables = soup.select('center > table')
    color_table = None
    for table in tables:
        prev = table.find_previous_sibling()
        if prev and prev.name == 'p':
            color_table = table
            break
    return color_table


# Constants for the columns in the color table
COLOR_COLUMN = 3
ELEMENT_ID_COLUMN = 4


def convert_table_to_dict(table):
    """
    Convert the color table to a dictionary.

    Args:
        table (bs4.element.Tag): The color table element.

    Returns:
        dict: A dictionary mapping color IDs to lists of element IDs.
    """
    dict = {}
    rows = table.find_all('tr')
    for row in rows:
        data = row.find_all('td')
        if len(data) < 5:
            continue
        color_name = data[COLOR_COLUMN].text
        color_name = color_name.strip().replace('\xa0', '')
        if color_name not in colors_by_name.keys():
            continue
        color_id = colors_by_name[color_name]
        element_id = data[ELEMENT_ID_COLUMN].text
        element_id = element_id.strip().replace('\xa0', '')
        if dict.get(color_id):
            dict[color_id].append(element_id)
        else:
            dict[color_id] = [element_id]
    return dict


def main():
    """
    Entrypoint for test.

    You can run this script from the command line to test the functionality of the API.
    """
    if len(sys.argv) != 2:
        print("Usage: python grab_color_info.py <number>")
        return
    number = sys.argv[1]
    color_dict = get_color_dict_for_part(number)
    print(f"Color dict for part {number}: {color_dict}")


if __name__ == "__main__":
    main()
