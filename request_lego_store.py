import sys
import logging
import requests

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
    centAmount
    currencyCode
  }
}
'''

def get_lego_store_result_for_element_id(element_id):
    url = "https://www.lego.com/api/graphql/PickABrickQuery" 
    json_body = {
        "operationName": "PickABrickQuery",
        "variables": {"input": {"perPage": 10, "query": str(element_id)}},
        "query": QUERY
    }
    headers = {}

    response = requests.post(url, json=json_body, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    response_json = response.json()

    results = response_json['data']['searchElements']['results']
    if len(results) < 1:
        logging.error(f"Did not receive result for element ID: {element_id}")
        return
    print(f"Received {len(results)} results for element ID: {element_id}, returning the first one.")
    return results[0]


def main():
    """
    Main function to handle command line argument and make the GraphQL request.
    """
    if len(sys.argv) != 2:
        print("Usage: python request_lego_pab.py <element_id>")
        sys.exit(1)

    element_id = int(sys.argv[1])

    print(get_lego_store_result_for_element_id(element_id))


if __name__ == "__main__":
    main()
