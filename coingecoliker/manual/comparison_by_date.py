import json
import os
from datetime import datetime, timedelta
import datetime as DT
from pymongo import MongoClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

# load json data and return {name_coin: people like this}
def load_json(file_name): 
    with open(os.path.join(BASE_DIR, 'coingecko', 'static', 'parsers', file_name), 'r') as f:
        data_dict = json.load(f)
    return data_dict

def load_MongoDB(data_name):
    db = client.parsers
    data_ = db[data_name]
    data_dict = data_.find_one()
    data_dict.pop('_id')
    return data_dict

# compare data. Function return { coin_name: {total_val = var, different_val = var} }
def comparison_dict(last_data, new_data):
    compare_data = {}
    for key in new_data:
        if not key in last_data.keys():
            print('Add new coin: ', key)
            try:
                compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': 0}
            except:
                if new_data.get(key) !=  'Error':
                    compare_data[key] = {'total_val': 0, 'different_val': 0}
        else:
            try:
                compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': (int(new_data.get(key)) - int(last_data.get(key)))}
            except:
                if new_data.get(key) !=  'Error':
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': 0}
                else:
                    print('Coin is not defind on coingecko.com: ', key)
    return sort_dict(compare_data)

def save_json(compare_data):
    date_t = datetime.now()
    date = date_t.strftime("%Y-%m-%d_%H:%M")
    file_name = ('%s_result.json' % date)
    path = os.path.join(BASE_DIR, 'coingecko', 'static', 'result', file_name)
    print(path)
    with open(path, 'w') as f:
        json.dump(compare_data, f, indent=4)

def sort_dict(compare_data):
    sort = {}
    for key, value in compare_data.items():
        sort[key] = value['total_val']
    sorted_={k: v for k, v in sorted(sort.items(),reverse=True, key=lambda item: item[1])}
    sort_compare_data = {}
    for key in sorted_:
        sort_compare_data[key] = compare_data.get(key)
    return sort_compare_data

def update_files(last_file, new_file):
    os.system('mv {} {}'.format(new_file, last_file))

# find all parse files and return list of files sorted by date [now_file, hour_ago_file, ..... , old_file]
def find_all_files():
    path = os.path.join(BASE_DIR, 'coingecko', 'static', 'parsers')
    file_names = os.listdir(path=path)
    file_names = sorted(file_names, reverse=True)
    return file_names

# find all parse date from MongoDB and return list of data sorted by date [nowe_d, hour_ago_d, ..... , old_d]
def find_all_date_MongoDB():
    db = client.parsers
    data_names = db.list_collection_names()
    data_names = sorted(data_names, reverse=True)
    return data_names

def count_f(all_parse_files, counter):
    #text = all_parse_files[0].split('.')[0] # use it without MongoDB
    text = all_parse_files[0]
    date_t = datetime.strptime(text, '%Y-%m-%d_%H:%M')
    if counter == 0:
        var_d = date_t - timedelta(hours=1)
    else:
        var_d = date_t - timedelta(counter)
    var_s = var_d.strftime('%Y-%m-%d_%H')    
    for name in all_parse_files:
        if var_s in name:
            return name
    if counter != 0:
        var_s =var_d.strftime('%Y-%m-%d')
        for name in all_parse_files:
            if var_s in name:
                return name
    return 0

# select from all parse files 4 name of files [now_file, hour_ago_file, day_ago_file, week_ago_file]
def select_four_files(all_parse_files):
    now_f = all_parse_files[0]
    hour_ago_f = count_f(all_parse_files, 0)
    day_ago_f = count_f(all_parse_files, 1)
    week_ago_f = count_f(all_parse_files, 7)
    return [now_f, hour_ago_f, day_ago_f, week_ago_f]

def main():
    #all_parse_files = find_all_files()
    all_parse_files = find_all_date_MongoDB()
    print(all_parse_files)
    selected_list_parse = select_four_files(all_parse_files)
    print(selected_list_parse)
    #new_data = load_json(selected_list_parse[0]) # use it without MongoDB
    new_data = load_MongoDB(selected_list_parse[0])
    compair_dict = {}
    for key in new_data:
        compair_dict[key] = {'total_val': 0}
    i = 1
    # todo - if not file in selected_list_parse[yes, yes, no, no] it compqir will not work - todo check
    while i < 4:
        if selected_list_parse[i] == 0:
            last_data = new_data
        else:
            #last_data = load_json(selected_list_parse[i]) #use it without MongoDB
            last_data = load_MongoDB(selected_list_parse[i])
        var_dict = comparison_dict(last_data, new_data)

        for key in var_dict:
            compair_dict[key].update({'total_val': int(var_dict.get(key)['total_val']), 'diff-{}'.format(i): var_dict.get(key)['different_val']})
        i = i + 1
    save_json(sort_dict(compair_dict))
    print(len(compair_dict.keys()))

    
    #if not os.path.isfile(last_file):
    #    print('File coingecko_table_last.json is not exist')
    #    return None

    #if not os.path.isfile(new_file):
    #    print('File coingecko_table_new.json is not exist.')
    #    print('YOU NEED TO RUN SCRAPER')
    #    return None

    #last_data = load_json(last_file)
    #new_data = load_json(new_file)
    #save_json(comparison_dict(last_data, new_data))
    #update_files(last_file, new_file)


#------------------------------------------

main()



# todo
# last file = new file
