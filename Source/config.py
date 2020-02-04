# List of simple to collect features
snippet_features = ["title",
                    "publishedAt",
                    "channelId",
                    "channelTitle",
                    "categoryId"]

# Any characters to exclude, generally these are things that become problematic in CSV files
unsafe_characters = ['\n', '"']

# Used to identify columns, currently hardcoded order
header = ["video_id"] + snippet_features + ["trending_date", "tags", "view_count", "likes", "dislikes",
                                            "comment_count", "thumbnail_link", "comments_disabled",
                                            "ratings_disabled", "description","duration"]

columnas = "video_id,title,publishedAt,channelId,channelTitle,categoryId,trending_date,tags,view_count,likes,dislikes,comment_count,thumbnail_link,comments_disabled,ratings_disabled,description,duration,country,subscriptions,NumeroVideosCanal"
country_codes = ['US', 'GB', 'CA', 'ES']

# TODO: Fill the gaps
# API configuration
api_key = ''

# Storage configuration
output_dir = ''  # Storage path for CSV files

# MySQL user and password
sql_user = ''  # MySql user
sql_pw = ''  # MySql password
