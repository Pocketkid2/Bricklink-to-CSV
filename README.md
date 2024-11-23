# BrickLink XML partslist to LEGO Pick-a-Brick CSV/JSON partslist converter

This project contains the following Python 3 scripts:

1. `save_me_money.py` - Take a BrickLink exported cart set, and pull out a LEGO Pick-A-Brick order for any lot where the parts can be found cheaper on LEGO's site!
2. `convert.py` - Simpler script, converts all items in a BrickLink XML wishlist, and converts to LEGO Pick-A-Brick order set (only for parts that are available there, the rest will be exported back to a BrickLink XML)
3. `merge.py` - Even simpler script, takes in a sequence of BrickLink XML wishlist files, and merges them into a single one

This tool makes a lot of web requests to get all the information from BrickLink and LEGO, and caches those results in a local SQLite database. Subsequent re-runs on the same inputs will be much faster as a result, although it is recommended to purge the database file from time to time as the availability and pricing information on LEGO, and especially BrickLink, can change at any time without notice.
