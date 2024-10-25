import sys
import shelve
import requests
from bs4 import BeautifulSoup
from colors import colors_by_name


def shelve_it(file_name):
    def decorator(func):
        def new_func(param):
            with shelve.open(file_name) as d:
                if param not in d:
                    d[param] = func(param)
                return d[param]

        return new_func
    return decorator


@shelve_it('webpage_cache.shelve')
def get_webpage_for_part(design_id):
    try:
        url = f"https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo={design_id}"
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


def find_color_table_in_page(page_content):
    soup = BeautifulSoup(page_content, 'lxml')
    tables = soup.select('center > table')
    color_table = None
    for table in tables:
        prev = table.find_previous_sibling()
        if prev and prev.name == 'p':
            color_table = table
            break
    return color_table


COLOR_COLUMN = 3
ELEMENT_ID_COLUMN = 4
def convert_table_to_dict(table):
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
    if len(sys.argv) != 2:
        print("Usage: python grab_color_info.py <number>")
        return
    number = sys.argv[1]
    response_content = get_webpage_for_part(number)
    color_table = find_color_table_in_page(response_content)
    if not color_table:
        print("Could not find color table")
        return
    color_dict = convert_table_to_dict(color_table)


if __name__ == "__main__":
    main()