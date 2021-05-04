"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries.
"""


import xml.etree.cElementTree as ET
import pprint
import re
import json


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


created = [ "version", "changeset", "timestamp", "user", "uid"]

mapping = { "St.": "Street", "Ave": "Avenue", "Rd.": "Road"}


def shape_element(element):
    
    if element.tag == "node" or element.tag == "way":
        
        for i in ['node', 'way']:
            
            for item in element.iter(i):
                node = {}
                node['id'] = item.attrib['id']
                node['type'] = item.tag
                node['visible'] = item.attrib['visible']
                
                node['created'] = {}
                for e in created:
                    node['created'][e] = item.attrib[e]
                
                node['address'] = {}
                for tag in item.iter('tag'):
                    if lower_colon.search(tag.attrib['k']) and tag.attrib['k'].startswith('addr'):
                        node['address'][tag.attrib['k'].lstrip('addr:')] = update_name(tag.attrib['v'])
                    elif lower.search(tag.attrib['k']):
                        node[tag.attrib['k']] = tag.attrib['v']
                    
                if i == 'node':
                    node['pos'] = [float(item.attrib['lat']), float(item.attrib['lon'])]
                else:
                    node['node_refs'] = []
                    for nd in item.iter('nd'):
                        node['node_refs'].append(nd.attrib['ref'])
                        
                if node['address'] == {}:
                    del node['address']
                   
        return node
    else:
        return None


def process_map(file_in):
    
    file_out = "{0}.json".format(file_in)
    data = []
    with open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                fo.write(json.dumps(el, indent=4))
                
    return data


def update_name(name):

    for key in mapping.keys():
        if name.endswith(key):
            name = name.strip(key)
            name = name + mapping[key]
            
    return name


def mongo_insert(data, db):
    db.map.insert_many(data)
        

def test():
    
    data = process_map('example_addr.osm')
    pprint.pprint(data)

    correct_first_element = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z" }}
  
    assert data[0] == correct_first_element
    assert data[-1]["address"] == {
                                    "street": "West Lexington Street", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", 
                        "2199822369", "2199822370", "2199822284", "2199822281"] 


if __name__ == "__main__":
    test()
    
    data = process_map('example_addr.osm')
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.examples
    
    mongo_insert(data, db)