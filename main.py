import csv
import xml.etree.ElementTree as ET

from colors import colors

def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    parts = []

    for item in root:
        part = {} 
        for data in item:
            if data.tag == 'ITEMID':
                part['item'] = data.text
            if data.tag == 'COLOR':
                part['color_id'] = data.text
                part['color'] = colors[int(part['color_id'])]
            if data.tag == 'MINQTY':
                part['quantity'] = data.text
        
        parts.append(part)
    
    return parts

def export_csv(data, path):
    fields = ['item', 'color_id', 'color', 'quantity']

    with open(path, 'w', newline='') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames = fields) 
  
        writer.writeheader() 
  
        writer.writerows(data) 

def main():
    data = parse_xml('data.xml')
    export_csv(data, 'data.csv') 

if __name__ == '__main__':
    main()