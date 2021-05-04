"""
Your task in this exercise is to parse the file, process only the fields that
are listed in the FIELDS dictionary as keys, and return a list of dictionaries
of cleaned values. The set contains data about Arachnid class animals.
"""


import csv
import json
import pprint
import re


DATAFILE = 'arachnid.csv'

FIELDS = {'rdf-schema#label': 'label',
         'URI': 'uri',
         'rdf-schema#comment': 'description',
         'synonym': 'synonym',
         'name': 'name',
         'family_label': 'family',
         'class_label': 'class',
         'phylum_label': 'phylum',
         'order_label': 'order',
         'kingdom_label': 'kingdom',
         'genus_label': 'genus'}

CLASSIFIC = ['kingdom', 'family', 'order', 'phylum', 'genus', 'class']


def process_file(filename, fields, classific):

    process_fields = fields.keys()
    data = []
    
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for i in range(3):
            l = next(reader)

        for row in reader:
            arachnid = {}
            arachnid['classification'] = {}
            
            for field, val in row.items():
                
                field, val = field.strip(), val.strip()
                
                if field == 'synonym' and val != 'NULL':
                    val = parse_array(val)              
                    
                if val == 'NULL':
                    val = None
                
                if field == 'rdf-schema#label':
                    val = clean_label(val)
                
                if field == 'name' and (val == None or not val.isalnum()):
                    val = row['rdf-schema#label']
                    val = clean_label(val)
                    
                if field in process_fields:
                    field = fields[field]
                    
                    if field in classific:
                        arachnid['classification'][field] = val
                    else:
                        arachnid[field] = val
                        
            data.append(arachnid)
            
    return data


def parse_array(v):
    if v[0] == '{' and v[-1] == '}':
        v = v.lstrip('{').rstrip('}')
        v = v.split('|')
        v = [i.lstrip('* ') for i in v]
        return v
    return[v]


def clean_label(v):
    label_descr = re.compile(r'[(][a-z]*[)]$')
    if label_descr.search(v):
        v = v.rstrip(label_descr.search(v).group())
        v = v.rstrip()
    return v


def create_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        
        
def test():
    data = process_file(DATAFILE, FIELDS, CLASSIFIC)
    print("Your first entry:")
    pprint.pprint(data[0])
    
    first_entry = {
        "synonym": None, 
        "name": "Argiope", 
        "classification": {
            "kingdom": "Animal", 
            "family": "Orb-weaver spider", 
            "order": "Spider", 
            "phylum": "Arthropod", 
            "genus": None, 
            "class": "Arachnid"
        }, 
        "uri": "http://dbpedia.org/resource/Argiope_(spider)", 
        "label": "Argiope", 
        "description": "The genus Argiope includes rather large and spectacular spiders that often have a strikingly coloured abdomen. These spiders are distributed throughout the world. Most countries in tropical or temperate climates host one or more species that are similar in appearance. The etymology of the name is from a Greek name meaning silver-faced."
    }

    assert len(data) == 76
    assert data[0] == first_entry
    assert data[17]["name"] == "Ogdenia"
    assert data[48]["label"] == "Hydrachnidiae"
    assert data[14]["synonym"] == ["Cyrene Peckham & Peckham"]


if __name__ == "__main__":
    test()
   
    