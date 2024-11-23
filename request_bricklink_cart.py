"""Bricklink Cart Request.

This module contains the API needed for making web requests to BrickLink.com
and obtaining information about a certain store id and lot id (items in a cart).
"""

import sys
import logging
import requests


def get_part_and_price_for_lot(store_id, lot_id):
    """
    Get the part and price for a given store and lot ID.

    Args:
        store_id (Union[int, str]): The BrickLink store ID.
        lot_id (Union[int, str]): The BrickLink store lot ID.

    Returns:
        dict: The part and price data from the request.
    """
    return parse_json(get_json_for_store_and_lot_id(store_id, lot_id))


def parse_json(json_data):
    """
    Parse the JSON data from a request.

    Args:
        json_data (dict): The JSON data from the request.

    Returns:
        tuple: The part and price data.
    """
    return (json_data['itemNo'], json_data['colorID'], float(json_data['nativePrice'][4:]))


def get_json_for_store_and_lot_id(store_id, lot_id):
    """
    Get the JSON data for a given store.

    Args:
        store_id (Union[int, str]): The BrickLink store ID.
        lot_id (Union[int, str]): The BrickLink store lot ID.

    Raises:
        http_err: An HTTP error occurred.
        err: An error occurred.

    Returns:
        dict: The JSON data from the request.
    """
    try:
        url = f"https://store.bricklink.com/ajax/clone/store/item.ajax?invID={lot_id}&sid={store_id}&wantedMoreArrayID="
        logging.info(f"Fetching {url}")
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Host': 'store.bricklink.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Error code: {response.status_code}")
        logging.error(f"Error data: {response.text}")
        raise http_err
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        raise err


def main():
    """
    Entrypoint for test.

    You can run this script from the command line to test the functionality of the API.
    """
    if len(sys.argv) != 3:
        print("Usage: python request_bricklink_cart.py <store_id> <lot_id>")
        sys.exit(1)
    store_id = sys.argv[1]
    lot_id = sys.argv[2]
    print(parse_json(get_json_for_store_and_lot_id(store_id, lot_id)))


if __name__ == "__main__":
    main()
