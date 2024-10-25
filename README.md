# BrickLink XML to LEGO Pick-a-Brick CSV/JSON

## The problem
Most LEGO builds published online give you an XML file to upload to BrickLink so you can search stores for the parts. Which is great, except that sometimes the LEGO pick-a-brick store is actually cheaper, particularly for builds with large numbers of simple pieces where you want to bulk order.

Unfortunately, this is not as simple as converting the XML data to CSV/JSON, as BrickLink focuses entirely on Design ID (unique to part shape/mold) and Color code, whereas the LEGO site is looking for Element ID (unique to combination of mold and color and any other markings or configuration), which is not trivial to find. Sometimes it is the design id + color code, but other times it is something completely different.

## The solution
The good news is, BrickLink does keep track of which parts are available in which colors, and users have reported what the "part color code" is (element ID), and if we can figure out how to map the design ID + color code to that element ID, we can be successful. Whether or not we can use the BrickLink API or will have to webscrape for it (since it appears to be a very informal reporting system) remains to be seen.

## Resources
1. Bricklink Color Guide - This provides the mapping of Color ID to Color Name and other information that we don't need
```
https://www.bricklink.com/catalogColors.asp
```
2. Bricklink Color Images (per-part) - This provides a table of Color Name to "Part Color Code" (Element ID) mappings
```
https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=32062
```

## Current functionality
1. Can choose between LEGO Pick-a-Brick JSON or CSV
2. Normal parts work beautifully; printed and rare parts, not so much, but that's to be expected
3. Conversion can take some time (15-20 for large lists) but progress is displayed
4. Webpage results from BrickLink are cached so the same web request does not need to be made again (the primary speed bottleneck)

## Known issues
1. Cache stores webpage results, leading to much larger cache file size than is necessary
2. No error printout if the algorithm can't find Element IDs
3. No way of checking if LEGO actually sells given Element ID
4. No way of checking if LEGO accepts more than one Element ID, leading to potential duplicates
5. Parallelize web requests?