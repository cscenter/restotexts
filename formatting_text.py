import re
from pymongo import MongoClient
import spacy
import pymorphy2
mclient = MongoClient('localhost', 27017)
db = mclient.restotexts
posts = db.posts

nlp = spacy.load('ru2')
morph = pymorphy2.MorphAnalyzer()

for post in posts.find():
    
    text = post.get('text')
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"[^A-Za-zА-Яа-я0-9Ёё.]+", '', text)
    text = text.lower()
    
    doc = nlp(text)
    l = [word.lemma_ for word in doc]
    for word in l:
        p = morph.parse(word)[0]
        t = p.tag
        i = l.index(word)
        
        if 'NPRO' in t\
                or 'PRED' in t\
                or 'PREP' in t\
                or 'CONJ' in t\
                or 'PRCL' in t\
                or 'INTJ' in t\
                or 'Apro' in t\
                or 'Ques' in t\
                or 'Prdx' in t\
                or 'Dmns' in t:
            l.pop(i)
            
    text = ' '.join([word for word in l])
    
    text = re.sub(" +", " ", text)
    
    id = post.get("_id")
    db.posts.update_one({"_id": id}, {"$set": {"formatted_text": text}})
