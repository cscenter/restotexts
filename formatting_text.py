import re
import pymorphy2
from pymongo import MongoClient

morph = pymorphy2.MorphAnalyzer()

mclient = MongoClient('localhost', 27017)
db = mclient.restotexts
mposts = db.posts


def norm_word(word):
    return morph.parse(word)[0].normal_form


def trashpos(word):
    tag = morph.parse(word)[0].tag
    if 'NPRO' in tag\
            or 'PRED' in tag\
            or 'PREP' in tag\
            or 'CONJ' in tag\
            or 'PRCL' in tag\
            or 'INTJ' in tag\
            or 'Apro' in tag\
            or 'Ques' in tag\
            or 'Prdx' in tag\
            or 'NUMR' in tag\
            or 'Dmns' in tag:
        return True
    else:
        return False


def format(text):
    text = re.sub(r"[^А-Яа-яЁё ]+", ' ', text)
    return text.lower()


def del_spaces(text):
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def text2list(text):
    text = format(text)
    list = text.split(' ')
    return list


def list2text(list):
    text = ' '.join([word for word in list])
    return text


file_trash = open('trash.txt', 'r')
trash = text2list(file_trash.read())

for post in mposts.find():
    id = post.get("_id")
    text = post.get('text')
    if text == "" or text is None:
        continue

    text = format(text)
    l = text2list(text)
    l = [norm_word(word) for word in l]

    to_delete = []
    for index, word in enumerate(l):
        if trashpos(word) or norm_word(word) in trash:
            to_delete.append(index)
            print(word.upper(), l)

    for index in sorted(to_delete, reverse=True):
        del l[index]

    text = del_spaces(list2text(l))
    db.posts.update_one({"_id": id}, {"$set": {"formatted_text": text}})

file_trash.close()
