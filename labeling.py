import numpy as np
import pprint
import re
from gensim.models import Word2Vec
from joblib import dump, load
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import BernoulliNB


Mclient = MongoClient('localhost', 27017)
Db = Mclient.restotexts
Posts = Db.posts
Posts.create_index([("formatted_text", "text")])

pipeline1 = [
    {"$match": {"corpus": "train", "category": None, "formatted_text":{"$ne": None}}},
    {"$sample": {"size": 300}}
]

pipeline2 = [
    {"$match": {"corpus": "train", "category": None, "$text": {"$search": "сладость"}}}, #poisk po slovy
    {"$sample": {"size": 50}}
]

#Posts.update_many({"category": ""}, {"$set":{"category": None}})

Texts = []
Labels = []

for post in Posts.find({"category":{"$ne": None}, "formatted_text": {"$ne": None}}):
    _id = post.get("_id")
    text = post.get("formatted_text")
    category = post.get("category")
    Texts.append(text.split())
    Labels.append(category)

Texts = np.array(Texts)
Labels = np.array(Labels)

Model = Word2Vec.load("modelBNB.w2v")
Clf_bnb = load("modelBNB.sk")


def new_vec_mean(text):
    return np.mean([Model.wv.word_vec(word) for word in text if word in Model.wv.vocab]
                      or [np.zeros(Model.vector_size)], axis=0).reshape(1, -1)


Data_mean = np.array([new_vec_mean(text) for text in Texts])

tfidf_transformer = TfidfTransformer().fit(Data_mean)
Data_tfidf = tfidf_transformer.transform(Data_mean)

for post in Posts.aggregate(pipeline2):
    _id = post.get("_id")
    text = post.get("text")
    formatted_text = post.get("formatted_text")
    formatted_text = formatted_text.split()

    New_vec = new_vec_mean(formatted_text)
    pred = Clf_bnb.predict(New_vec)

    print(pred[0], "?")
    text = re.sub(r"[^А-Яа-яA-Za-z0-9.,!?()Ёё\n ]+", ' ', text)
    pprint.pprint(text)
    ans = str(input())
    categ = ""

    if ans == "":
        categ = pred[0]

    if ans == "0":
        categ = str(input())

    if ans == " ":
        continue

    Model.train([formatted_text], total_examples=1, epochs=1)
    np.append(Texts, formatted_text)
    np.append(Data_mean, New_vec)
    np.append(Labels, categ)
    tfidf_transformer = TfidfTransformer().fit(Data_mean)
    Data_tfidf = tfidf_transformer.transform(Data_mean)
    Clf_bnb.partial_fit(Data_tfidf, Labels)

    Model.save("modelBNB.w2v")
    dump(Clf_bnb, "modelBNB.sk")
    Posts.update_one({"_id": _id}, {"$set": {"category": categ}})
