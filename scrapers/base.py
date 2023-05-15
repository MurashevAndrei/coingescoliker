from pymongo import MongoClient


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")
bearer_token = 'AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M'

def connect_db(name_db, name_collection):
    db = client[name_db]
    collection = db[name_collection]
    return collection


def load_mongo(name_db, name_collection, data_name, data_get='data'):
    db = connect_db(name_db, name_collection)
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get(data_get)
    return data_dict
