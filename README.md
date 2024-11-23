# BrickLink XML partslist to LEGO Pick-a-Brick CSV/JSON partslist converter

1. `save_me_money.py` - Take a BrickLink exported cart set, and pull out a LEGO Pick-A-Brick order for any lot where the parts can be found cheaper on LEGO's site!
2. `convert.py` - Simpler script, converts all items in a BrickLink XML wishlist, and converts to LEGO Pick-A-Brick order set (only for parts that are available there, the rest will be exported back to a BrickLink XML)
3. `merge.py` - Even simpler script, takes in a sequence of BrickLink XML wishlist files, and merges them into a single one
