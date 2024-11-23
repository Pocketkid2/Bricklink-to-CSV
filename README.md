# BrickLink XML partslist to LEGO Pick-a-Brick CSV/JSON partslist converter

This project contains the following Python 3 scripts:

1. `save_me_money.py` - Take a BrickLink exported cart file, and pull out a LEGO Pick-A-Brick order for any lot where the parts can be found cheaper on LEGO's site! It will spit out a .cart file that can be imported back into BrickLink, and a CSV file that can be used to create a Pick-A-Brick order on the official LEGO Pick-A-Brick site (look for the "Upload List" button)
2. `convert.py` - Simpler script, converts all items in a BrickLink XML wishlist/partslist, and converts to LEGO Pick-A-Brick order set (only for parts that are available there, the rest will be exported back to a BrickLink XML)
3. `merge.py` - Even simpler script, takes in a sequence of BrickLink XML wishlist files, and merges them into a single one

The two main scripts (`save_me_money.py` and `convert.py`) make a lot of web requests to get all the information from BrickLink and LEGO, and caches those results in a local SQLite database. Subsequent re-runs on the same inputs will be much faster as a result, although it is recommended to purge the database file from time to time as the availability and pricing information on LEGO, and especially BrickLink, can change at any time without notice.

**DISCLAIMER 1:** This project compares raw USD prices only. If you need this script to support other currencies, please file an issue on the GitHub issue tracker. 

**DISCLAIMER 2:** This project does not take shipping and handling prices into account. Thus, you will need to manually check the results to make sure you are actually getting a good deal. That being said, LEGO Pick-A-Brick does offer free shipping and handling if your order is above approximately $20, so for large projects it should almost always be a better option. For small projects, you may end up getting a worse deal since LEGO usually charges at least $7 for shipping/handling, and also your BrickLink carts may reduce in size to below the store minimum buy.
