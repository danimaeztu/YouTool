# -*- coding: utf-8 -*-
import requests
import sys
import time
import urllib.request
import json
import pandas as pd
import config as cf
import sqlalchemy
import pymysql  # Using virtual env this is the only way
pymysql.install_as_MySQLdb()

# Functions


def prepare_feature(feature):
    """Removes any character from the unsafe characters list
    and surrounds the whole item in quotes"""
    for ch in cf.unsafe_characters:
        feature = str(feature).replace(ch, "")
    return f'"{feature}"'


def api_request(page_token, country_code):
    """Builds the URL and requests the JSON from it"""
    request_url = f"https://www.googleapis.com/youtube/v3/videos?part=id,statistics,contentDetails,snippet{page_token}chart=mostPopular&regionCode={country_code}&maxResults=10&key={cf.api_key}"
    request = requests.get(request_url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()


def get_tags(tags_list):
    """Takes a list of tags, prepares each tag
    and joins them into a string by the pipe character"""
    return prepare_feature("|".join(tags_list))


def get_videos(items):
    """Get video data"""
    lines = []
    for video in items:
        comments_disabled = False
        ratings_disabled = False
        # We can assume something is wrong with the video if it has no statistics,
        # often this means it has been deleted, so we can just skip it
        if "statistics" not in video:
            continue

        video_id = prepare_feature(video['id'])
        # Snippet and statistics are sub-dicts of video, containing the most useful info
        snippet = video['snippet']
        statistics = video['statistics']
        contentDetails = video['contentDetails']

        # This list contains all of the features in snippet that are 1 deep and require no special processing
        features = [prepare_feature(snippet.get(feature, "")) for feature in cf.snippet_features]
        # The following are special case features which require unique processing, or are not within the snippet dict
        description = snippet.get("description", "")
        thumbnail_link = snippet.get("thumbnails", dict()).get("default", dict()).get("url", "")
        trending_date = time.strftime("%y.%d.%m")
        tags = get_tags(snippet.get("tags", ["[none]"]))
        view_count = statistics.get("viewCount", 0)

        duration = prepare_feature(contentDetails.get("duration", ["[none]"]))

        # This may be unclear, essentially the way the API works is that if a video has comments or ratings disabled
        # then it has no feature for it, thus if they don't exist in the statistics dict we know they are disabled
        if 'likeCount' in statistics and 'dislikeCount' in statistics:
            likes = statistics['likeCount']
            dislikes = statistics['dislikeCount']

        else:
            ratings_disabled = True
            likes = 0
            dislikes = 0

        if 'commentCount' in statistics:
            comment_count = statistics['commentCount']
        else:
            comments_disabled = True
            comment_count = 0
        # Compiles all of the various bits of info into one consistently formatted line
        line = [video_id] + features + [prepare_feature(x) for x in [trending_date, tags, view_count, likes, dislikes,
                                                                     comment_count, thumbnail_link, comments_disabled,
                                                                     ratings_disabled, description, duration]]

        lines.append(",".join(line))
    return lines


def get_pages(country_code, next_page_token="&"):
    """iterate over page tokens"""
    country_data = []
    # Because the API uses page tokens (which are literally just the same function of numbers everywhere) it is much
    # more inconvenient to iterate over pages, but that is what is done here.
    while next_page_token is not None:
        # A page of data i.e. a list of videos and all needed data
        video_data_page = api_request(next_page_token, country_code)
        # Get the next page token and build a string which can be injected into the request with it, unless it's None,
        # then let the whole thing be None so that the loop ends after this cycle
        next_page_token = video_data_page.get("nextPageToken", None)
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token
        # Get all of the items as a list and let get_videos return the needed features
        items = video_data_page.get('items', [])
        country_data += get_videos(items)

    return country_data


def write_to_file(country_code, country_data):
    """Write data into CSV file"""
    print(f"Writing {country_code} data to file...")

    with open(f"{cf.output_dir}/{time.strftime('%y.%d.%m')}_{country_code}_videos.csv", "w+", encoding='utf-8') as file:
        for row in country_data:
            file.write(f"{row}\n")


def get_data():
    """Join functions"""
    for country_code in cf.country_codes:
        country_data = [",".join(cf.header)] + get_pages(country_code)
        write_to_file(country_code, country_data)


def info_canal(datos,nombre):
    """Get channel data"""
    subscriptions = []
    NumeroVideosCanal = []

    for i in datos['channelId']:
        # API connection
        data = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/channels?part=statistics&id="+i+"&key="+cf.api_key).read()
        # Reads json data
        # Number of channel subscriptors obtained using the channel ID
        subscriptions.append(json.loads(data)["items"][0]["statistics"]["subscriberCount"])
        # Number of channel videos obtained using the channel ID
        NumeroVideosCanal.append(json.loads(data)["items"][0]["statistics"]["videoCount"])

    datos['country'] = nombre
    datos['subscriptions'] = subscriptions
    datos['NumeroVideosCanal'] = NumeroVideosCanal

    datos.to_csv("{}/{}_{}_videos.csv".format(cf.output_dir, time.strftime('%y.%d.%m'),
                                              nombre), index=None, header=True)
    return(datos)

# Main code
get_data()

# Read data country by country
US = pd.read_csv("{}/{}_US_videos.csv".format(cf.output_dir, time.strftime('%y.%d.%m')), engine='python', encoding='latin_1')
GB = pd.read_csv("{}/{}_GB_videos.csv".format(cf.output_dir, time.strftime('%y.%d.%m')), engine='python', encoding='latin_1')
CA = pd.read_csv("{}/{}_CA_videos.csv".format(cf.output_dir, time.strftime('%y.%d.%m')), engine='python', encoding='latin_1')
ES = pd.read_csv("{}/{}_ES_videos.csv".format(cf.output_dir, time.strftime('%y.%d.%m')), engine='python', encoding='latin_1')

# Append channel data
US = info_canal(US,'US')
GB = info_canal(GB,'GB')
CA = info_canal(CA,'CA')
ES = info_canal(ES,'ES')

# Join countries data into one single dataset
GLOBAL = pd.concat([US, GB, CA, ES], sort=False)
GLOBAL = GLOBAL[GLOBAL['duration'].isnull() == False]  # Avoid some problematic NULL

# Connection to Mysql
mysql = "mysql://{}:{}@localhost/YouTool".format(
        cf.sql_user, cf.sql_pw)
engine = sqlalchemy.create_engine(mysql)
connection = engine.connect()

# Insert data into MariaDB Server
GLOBAL.to_sql('Trending_videos', con=connection, schema='YouTool',
              if_exists='append', index=False)

# Print the result
sql = """SELECT trending_date, country, COUNT(country) AS cantidad
         FROM Trending_videos
         WHERE trending_date = "{}"
         GROUP BY country;""".format(time.strftime("%y.%d.%m"))
result = pd.read_sql(sql, connection)
print(result)
