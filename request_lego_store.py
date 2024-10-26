import sys
import json
import requests


def get_lego_store_result_for_element_id(element_id):
    return {}


def make_graphql_request(json_body, headers):
    """
    Make a GraphQL request and return the response JSON.

    Args:
        query (str): The GraphQL query string.
        headers (dict): The request headers.

    Returns:
        dict: The response JSON object.
    """
    url = "https://www.lego.com/api/graphql/PickABrickQuery"  # Replace with the actual GraphQL endpoint
    response = requests.post(url, json=json_body, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


def parse_json(response_json):
    results = response_json['data']['searchElements']['results']
    if len(results) > 0:
        return results
    raise results


def main():
    """
    Main function to handle command line argument and make the GraphQL request.
    """
    if len(sys.argv) != 2:
        print("Usage: python request_lego_pab.py <element_id>")
        sys.exit(1)

    element_id = int(sys.argv[1])

    query = '''
query PickABrickQuery($input: ElementQueryInput!, $sku: String) {
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
  name
  deliveryChannel
  price {
    centAmount
    currencyCode
  }
  quantityInSet(sku: $sku)
  facets {
    color {  ...ElementFacetCategory}
  }
}

fragment ElementFacetCategory on ElementCategory {
  name
  key
}
'''

    json_body = {
        "operationName": "PickABrickQuery",
        "variables": {"input": {"perPage": 10, "query": str(element_id)}},
        "query": query,
    }

    # Define the request headers
    headers = {}

    try:
        response_json = make_graphql_request(json_body, headers)
        parse_json(response_json)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
