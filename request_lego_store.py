"""LEGO Pick-A-Brick Request.

This module contains the API needed for making web requests to LEGO.com
and obtaining Pick-A-Brick store results for a part number (Element ID).
"""

import sys
import logging
from curl_cffi import requests

QUERY = '''
query PickABrickQuery($input: ElementQueryInput!) {
  searchElements(input: $input) {
    results {
      ...ElementLeaf
    }
    total
    count
  }
}
fragment ElementLeaf on SearchResultElement {
  id
  maxOrderQuantity
  deliveryChannel
  price {
    formattedAmount
    currencyCode
  }
}
'''


def get_lego_store_result_for_element_id(element_id):
    """
    Get the Pick-A-Brick store results for a given part number (Element ID).

    Args:
        element_id (int): The part number (Element ID).

    Returns:
        dict: A dictionary containing the store results for the given part number.
    """
    url = "https://www.lego.com/api/graphql/PickABrickQuery"
    json_body = {
        "operationName": "PickABrickQuery",
        "variables": {"input": {"perPage": 10, "query": str(element_id)}},
        "query": QUERY
    }
    headers = {
        "Referer": f"https://www.lego.com/en-us/pick-and-build/pick-a-brick?query={str(element_id)}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.post(url, json=json_body, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    response_json = response.json()

    results = response_json['data']['searchElements']['results']
    if len(results) < 1:
        logging.warning(f"Did not receive result for element ID: {element_id}")
        return
    logging.info(f"Received {len(results)} results for element ID: {element_id}, returning the first one.")
    return results[0]


def main():
    """
    Entry point for test.

    You can run this script from the command line to test the functionality of the API
    """
    if len(sys.argv) != 2:
        print("Usage: python request_lego_store.py <element_id>")
        sys.exit(1)

    element_id = int(sys.argv[1])

    print(get_lego_store_result_for_element_id(element_id))


if __name__ == "__main__":
    main()
