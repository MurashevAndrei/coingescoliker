from pymongo import MongoClient
from datetime import datetime, timedelta
import datetime as DT

MONGO_DB = "mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority"
client = MongoClient(MONGO_DB)



def load_MongoDB():
    db = client.test
    data_ = db['each_hour']
    data_dict = data_.find()
    result = {}
    for coins_for_hour in data_dict[:300]:
        for coin, likes in coins_for_hour['data'].items():
            if coin in result and likes != 'Error':
                result[coin].append(likes)
            elif likes != 'Error':
                result.setdefault(coin, []).append(likes)
    r = {}
    r['data'] = result
    return r

def one_load_MongoDB(list_all_date):
    db = client.test.each_hour
    data_dict = db.find()
    result = {}
    for coins_for_hour in data_dict:
        if coins_for_hour['_id'] in list_all_date:
            print(coins_for_hour['_id'])
            for coin, likes in coins_for_hour['data'].items():
                if coin in result and likes != 'Error':
                    result[coin].append(likes)
                elif likes != 'Error':
                    result.setdefault(coin, []).append(likes)
    r = {}
    r['data'] = result
    return r

# find all parse date from MongoDB and return list of data sorted by date [nowe_d, hour_ago_d, ..... , old_d]
def find_all_date_MongoDB():
    db = client.test
    data_db = db['list_ids']
    data_names = data_db.find_one()
    return sorted(data_names['ids'], reverse=True)

def create_list_of_date(data):
    gen_date = datetime.strptime(data[0], '%Y-%m-%d_%H:%M')
    last_date = datetime.strptime(data[-1], '%Y-%m-%d_%H:%M')
    result_list = [data[0]]
    while gen_date > last_date:
        gen_date = gen_date - timedelta(1)
        gen_s = gen_date.strftime('%Y-%m-%d')
        for name in data:
            if gen_s in name:
                result_list.append(name)
                break
    return result_list

def save_to_DB(result):
    db = client.markets
    coll = db['grafiks']
    x = coll.delete_many({})
    x = coll.insert_one(result)

    #--------------------------------
    #              MAIN
    #-------------------------------
if __name__ == '__main__':
    list_all_date = create_list_of_date(find_all_date_MongoDB())
    #print(one_load_MongoDB(sorted(list_all_date, reverse=True)))
    save_to_DB(one_load_MongoDB(list_all_date))
