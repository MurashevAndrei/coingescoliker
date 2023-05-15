import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)

# load json data and return {name_coin: people like this}
def load_json(file_name): 
    with open(file_name, 'r') as f:
        data_dict = json.load(f)
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

def main(last_file, new_file):
    if not os.path.isfile(last_file):
        print('File coingecko_table_last.json is not exist')
        return None

    if not os.path.isfile(new_file):
        print('File coingecko_table_new.json is not exist.')
        print('YOU NEED TO RUN SCRAPER')
        return None

    last_data = load_json(last_file)
    new_data = load_json(new_file)
    save_json(comparison_dict(last_data, new_data))
    update_files(last_file, new_file)


#------------------------------------------

last_file = 'coingecko_table_last.json'
new_file = 'coingecko_table_new.json'

main(last_file, new_file)



# todo
# last file = new file
