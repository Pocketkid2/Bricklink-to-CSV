# BrickLink to LEGO Pick-a-Brick Converter

## Introduction

This tool is designed to help LEGO enthusiasts convert their BrickLink XML parts lists into a format that can be uploaded to LEGO's Pick-a-Brick store. This process involves web scraping to map BrickLink codes to LEGO codes and handles various issues that may arise, especially with larger builds. Disclaimer: Most partslists will probably contain items that LEGO Pick-A-Brick does not sell, and in that case, a new BrickLink XML partslist will be created containing just those parts which you can feed back into BrickLink.

## Purpose

The main purpose of this project is to:
1. Convert BrickLink XML parts lists into CSV or JSON files.
2. Map BrickLink part codes to LEGO part codes.
3. Handle potential issues with data conversion and ensure compatibility with LEGO's Pick-a-Brick store.

## How It Works

The script performs the following steps:

1. **Parse the Input XML File**: Reads the BrickLink XML parts list.
2. **Identify Unique Design IDs**: Finds all unique design IDs from the parts list.
3. **Check Database for Existing Entries**: Determines which design IDs are not already in the local database.
4. **Fetch Missing Design IDs from BrickLink**: Requests missing design IDs from BrickLink and updates the database.
5. **Create a Master List of Element IDs**: Compiles a list of all potential LEGO element IDs.
6. **Check Database for LEGO Store Entries**: Identifies which element IDs are not in the LEGO Pick-a-Brick database.
7. **Fetch Missing Element IDs from LEGO Store**: Requests missing element IDs from LEGO's Pick-a-Brick store and updates the database.
8. **Resolve Data Issues**: Handles any issues with the data, such as parts not available in the LEGO store.
9. **Export Data**: Exports the final data to CSV or JSON files.

## How to Use

### Prerequisites

- Python installed on your computer.
- Required Python libraries installed (e.g., `requests`, `beautifulsoup4`, `concurrent.futures`).

### Steps to Run the Script

1. **Prepare Your Environment**:
   - Ensure you have Python installed.
   - Install the required libraries using the following command:
     ```sh
     pip install -r requirements.txt
     ```

2. **Prepare Your Input XML File**:
   - Obtain your BrickLink XML parts list and save it to a file. When viewing the list in the browser, just click the "Download" button and mark the location.

3. **Run the Script**:
   - Open your terminal or command prompt.
   - Navigate to the directory where the script is located.
   - Run the script with the following command:
     ```sh
     python convert.py input.xml output.csv
     ```
   - Replace `input.xml` with the path to your input XML file and `output.csv` with the desired output file path.

### Command-Line Arguments

- `input_xml`: Path to the input XML file.
- `output_file`: Path to the output file (CSV or JSON).
- `-l, --log_file`: Path to the log file (default: `log.txt`).
- `-db, --database_file`: Path to the SQLite database file (default: `part_info.db`).
- `-pb, --purge_bricklink`: Purge the BrickLink table in the database before processing the XML.
- `-pl, --purge_lego_store`: Purge the LEGO Pick-a-Brick table in the database before processing the XML.

### Example Usage

```sh
python convert.py input.xml output.csv -l my_log.txt -db my_database.db
```