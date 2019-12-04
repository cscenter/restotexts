import re
from pymongo import MongoClient
mclient = MongoClient('localhost', 27017)
db = mclient.restotexts
posts = db.posts

for post in posts.find():
    text = post.get('text')
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[^A-Za-zА-Яа-я0-9 .]+", '', text)
    text = re.sub(" +", " ", text)
    text = text.lower()
    id = post.get("_id")
    db.posts.update_one({"_id": id}, {"$set": {"formatted_text": text}})