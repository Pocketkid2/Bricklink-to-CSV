import sys
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


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

def url_for_part_catalog_colors(design_id):
    return f"https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo={design_id}"


@shelve_it('webpage_cache.shelve')
def get_webpage_for_part(design_id):
    try:
        url = url_for_part_catalog_colors(design_id)
        print(f"Fetching {url}...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"})
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.content
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Error code: {response.status_code}")
        print(f"Error data: {response.text}")
        raise http_err
    except Exception as err:
        print(f"Other error occurred: {err}")
        raise err


def main():
    if len(sys.argv) != 2:
        print("Usage: python grab_color_info.py <number>")
        return

    number = sys.argv[1]
    response_content = get_webpage_for_part(number)

    soup = BeautifulSoup(response_content, 'lxml')

    tables = soup.select('center > table')

    color_table = None
    for table in tables:
        prev = table.find_previous_sibling()
    
        if prev and prev.name == 'p':
            color_table = table
            break

    
    if not color_table:
        print("Could not find color table")
        return
    
    print(f'Potential codes for each color of part {number}:')
    potential_codes_by_color = defaultdict(set)
    for row in color_table.find_all('tr')[1:]:
        columns = row.findChildren('td')
        if (len(columns) > 4):
            color = columns[3].text.strip()
            code = columns[4].text.strip()
            if color == ' By ':
                continue
            potential_codes_by_color[color].add(code)
            # print( color, code)
    print(potential_codes_by_color)
    # print(colors_by_name)


if __name__ == "__main__":
    main()