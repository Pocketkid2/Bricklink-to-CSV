# BrickLink XML partslist to LEGO Pick-a-Brick CSV/JSON partslist converter

## Abstract

This project is for people who want to convert their LEGO partslists (usually for custom builds) that are stored in a BrickLink-compatible XML file into a format that is compatible with LEGO's online Pick-A-Brick store. This is useful because LEGO's Pick-A-Brick store has a wide range of basic parts in many colors, and when buying large quantities this can actually save you money.

This program works by mapping BrickLink Design IDs and Color IDs to LEGO Element IDs that are found in their store. Any parts that are not available on the LEGO Pick-A-Brick store will be re-exported back to a separate XML partslist for separate buying. If the LEGO Pick-A-Brick store has more than one available option for a particular piece, it will choose the cheapest option, and if the price is the same, it will let you pick between the "Bestseller" store (located in the US with faster shipping) or the non-Bestseller store (located in the Netherlands with slow shipping).

The LEGO Pick-A-Brick store can handle either a CSV or JSON file, and both will be created. One order from the LEGO Pick-A-Brick store can have a maximum of 400 unique elements, 200 from the "Bestseller" store, and 200 from the non-Bestseller store. This program will account for this by splitting orders that would be too large.

## Tool 1: `convert.py`

### Abstract

This python script is the main entrypoint for the project, and does exactly what is described above. All results from web requests to BrickLink and LEGO Pick-A-Brick store are cached in a SQLite database file to speed up execution time as you continue to use the program. The output CSV and JSON files will have the same basename and path as the input XML file. You may or may not be prompted to select which LEGO Pick-A-Brick store you want a certain part to come from, if it exists in both stores for the same price.

### Python requirements

```
requests (web requests library)
bs4 (BeautifulSoup4 web scraping library)
lxml (XML parsing library)
```

I recommend you install via `python3 -m pip install -r requirements.txt`

### Command-line arguments

| argument name | required | description | default |
| ------------- | -------- | ----------- | ------- |
| `input_xml_file` | Yes | Path to the input XML file | N/A |
| `-ld` or `--log_dir` | No | Path to the folder where log files will be created | `logs` |
| `-db` or `--database_file` | No | Path to the SQLite database file | `part_info.db` |
| `-new` or `--bricklink_new` | No | If this flag is in the command, unavailable parts exported back to a separate BrickLink XML file will have their part condition set to "New", regardless of what they were set to in the input XML | N/A |
| `-used` or `--bricklink_used` | No | If this flag is in the command, unavailable parts exported back to a separate BrickLink XML file will have their part condition set to "Used", regardless of what they were set to in the input XML | N/A |
| `-pb` or `--purge_bricklink` | No | If this flag is in the command, the BrickLink cache table in the SQLite database will be removed, and the script will then exit. (You should not need this unless the format of the table changes in an update) | N/A |
| `-pl` or `--purge_lego_store` | No | If this flag is in the command, the LEGO Pick-A-Brick store cache table in the SQLite database will be removed, and the script will then exit. (You should not need this unless the format of the table changes in an update) | N/A |

## Tool 2: `merge.py`

### Abstract

This python script is for those situations where you want to combine smaller lists into a larger one to take advantage of the 400-element limit of the LEGO Pick-A-Brick store, and get better value for your money. It can take any number of input BrickLink XML files and combine all the data into a single output BrickLink XML files, including merging two separate quantities of the same part into a single entry. Ideally, you would run this before `convert.py`.

### Command-line arguments

| argument name | required | description | default |
| ------------- | -------- | ----------- | ------- |
| `output_xml_file` | Yes | The filename of the output BrickLink XML file | N/A |
| `input_xml_files` | At least one | Any number of filenames that are the input BrickLink XML files | N/A |
| `-l` or `--log_file` | No | Path to the log file | `log.txt` |
| `-new` or `--bricklink_new` | No | If this flag is in the command, all parts in the output BrickLink XML file will have their part condition set to "New", regardless of what they were set to in the input XML | N/A |
| `-used` or `--bricklink_used` | No | If this flag is in the command, all parts in the output BrickLink XML file will have their part condition set to "Used", regardless of what they were set to in the input XML | N/A |
