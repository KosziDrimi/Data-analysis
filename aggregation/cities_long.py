"""
Use an aggregation query to answer the following question. 
Which Region in India has the largest number of cities with longitude between
75 and 80?
"""

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def make_pipeline():
    
    pipeline = [ 
        {'$match' : {"country_label" : "India",
                    "wgs84_pos#long" : {"$gte" : 75, "$lte" : 80}}}, 
        {'$unwind' : "$isPartOf_label"},
        {'$group' : {'_id' : "$isPartOf_label",
                     'count' : {'$sum' : 1}}},             
        {'$sort' : {'count' : -1}},
        {'$limit' : 1} ]      
    
    return pipeline


def aggregate(db, pipeline):
    return [doc for doc in db.cities.aggregate(pipeline)]


if __name__ == '__main__':
    
    db = get_db('examples')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    
    import pprint
    pprint.pprint(result)
    
    projection = {'_id' : 0, 'name' : 1, 'wgs84_pos#long' : 1, 'isPartOf_label' : 1}
    for city in db.cities.find({"country_label" : "India"}, projection):
        pprint.pprint(city)
        
    assert len(result) == 1
    assert result[0]["_id"] == 'Karnataka'
    assert result[0]["count"] == 2
