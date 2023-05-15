from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def save_mongo(dict_for_save, name):
    #date_t = datetime.utcnow()
    #name = date_t.strftime("%Y-%m-%d_%H:%M")
    #coins =  {'bitcoin' : 200, 'eth': 300}
    #dict_coin = {'time' : name, 'data': coins}
    db = client.test
    pars_data = db[name]
    pars_data.insert_one(dict_for_save)
    print('ok')

def load_mongo():
    db = client.test
    data_ = db['each_hour']
    data_dict = data_.find()
    list_of_date = []
    i = 0
    for x in data_dict:
        for key in x.keys():
            if key == '_id':
                print(i)
                list_of_date.append(x.get(key))
                i = i+1
    return sorted(list_of_date, reverse=True)            #print(x.get(key))

def load_MongoDB(data_name):
    db = client.parsers
    data_ = db[data_name]
    data_dict = data_.find_one()
    data_dict.pop('_id')
    if '404' in data_dict:
        data_dict.pop('404')
    if '520' in data_dict:
        data_dict.pop('520')
    if '999' in data_dict:
        data_dict.pop('999')
    if '1337' in data_dict:
        data_dict.pop('1337')
    #print(data_dict)
    return data_dict

def compil_from_mongo():
    db = client.t.each_hour
    all_data = db.collection.find()
    print(all_data)
    for coin in all_data:
        print(coin['_id'])
    #data_names = db.list_collection_names()
    #print(data_names)

    """
    for i in data_names:
        dict_for_save = {}
        dict_for_save['_id'] = i
        dict_for_save['data'] = load_MongoDB(i)
        #save_mongo(dict_for_save, 'each_hour')
        print(a)
        a = a + 1
        print(dict_for_save)
    """
    #save_mongo(dict_for_save)


#compil_from_mongo()  # load data form parser and save it to each_hour
#save_mongo()
list_id = load_mongo() # get list of documents (date)
save_mongo({'ids': list_id}, 'list_ids') # get lext of doucumtnts (date)
