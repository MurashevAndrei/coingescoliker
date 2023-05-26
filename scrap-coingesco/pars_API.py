import get_links_with_API
import os
import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

API_key = 'QFHywxEK3zN1DahiEGb4Hmbaj'
API_secret_key = '2dsWuINjQTgO7SMnROqEZAZAWhE0bbHOJddrvwhlkc3tarUXd5'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M'
headers = {"Authorization": "Bearer {}".format(bearer_token)}


follows = 'https://api.twitter.com/1.1/followers/list.json?cursor=-1&screen_name=solecartier&skip_status=true&include_user_entities=false'
follows = 'https://api.twitter.com/1.1/followings/list.json?cursor=-1&screen_name=solecartier&skip_status=true&include_user_entities=false'
followers_id = 'https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name=solecartier&count=5000'
url = 'https://api.twitter.com/1.1/followers/list.json?cursor=-1&screen_name=solecartier&skip_status=true&include_user_entities=false'
GarryId = '44813348'
following = f'https://api.twitter.com/2/users/{GarryId}/following?' #max_results=1000'
get_user_id_by_screen_name = 'https://api.twitter.com/1.1/users/show.json?screen_name=solecartier'
screen_name = 'BTC_Archive'
get_followers_ids_by_scren_name = f'https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name={screen_name}&count=5000'

def create_url():
    query = "from:twitterdev -is:retweet"
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    tweet_fields = "tweet.fields=author_id"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
        query, tweet_fields
    )
    return url

def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

json_response = connect_to_endpoint(get_followers_ids_by_scren_name, headers)
#with open('followings.json', 'w') as f:
#    json.dump(json_response, f, indent=4, sort_keys=True)

print(json.dumps(json_response, indent=4, sort_keys=True))
print(len(json_response))
