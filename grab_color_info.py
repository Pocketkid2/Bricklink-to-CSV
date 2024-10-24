import sys
import requests
from bs4 import BeautifulSoup

import shelve
def shelve_it(file_name):
    def decorator(func):
        def new_func(param):
            with shelve.open(file_name) as d:
                if param not in d:
                    d[param] = func(param)
                return d[param]

        return new_func
    return decorator


# @shelve_it('webpage_cache.shelve')
def get_webpage_for_part(design_id):
    try:
        url = f"https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo={design_id}"
        print(f"Fetching {url}...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"})
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        print(response.content)
        return response.content
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Error code: {response.status_code}")
        print(f"Error data: {response.text}")
        return
    except Exception as err:
        print(f"Other error occurred: {err}")
        return


def main():
    if len(sys.argv) != 2:
        print("Usage: python grab_color_info.py <number>")
        return

    number = sys.argv[1]
    response_content = get_webpage_for_part(number)

    # print(response_content)

    soup = BeautifulSoup(response_content, 'html.parser')
    tables = soup.find_all('table')

    print(f"Number of tables found: {len(tables)}")
    
    rows = soup.select('td')
    print(rows)

    # for table in tables:
    #     print(f"Rows: {len(table.find_all('tr'))}")
    #     print(f"Cols: {len(table.find_all('td')) / len(table.find_all('tr'))}")
    #     print("\n")
    #     previous_sibling = table.find_previous_sibling()
    #     if previous_sibling and previous_sibling.name == 'p':
    #         print("Table following a <p> element:")
    #         rows = table.find_all('tr')
    #         for row in rows:
    #             cols = row.find_all('td')
    #             col_texts = [col.get_text(strip=True) for col in cols]
    #             print("\t".join(col_texts))
    #         print("\n")

if __name__ == "__main__":
    main()