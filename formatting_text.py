from pymongo import MongoClient
import pymorphy2
import re

Morph = pymorphy2.MorphAnalyzer()

Mclient = MongoClient('localhost', 27017)
Db = Mclient.restotexts
Mposts = Db.posts


def norm_word(word):
    return Morph.parse(word)[0].normal_form


def trashpos(word):
    pos_tags = ['NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'Apro', 'Ques', 'Prdx', 'NUMR', 'Dmns']
    tag = Morph.parse(word)[0].tag
    return any(pos_tag in tag for pos_tag in pos_tags)


def formatting(text):
    text = re.sub(r"[^А-Яа-яЁё ]+", ' ', text)
    return text.lower()


def del_spaces(text):
    text = re.sub(" +", " ", text)
    return text


def text2list(text):
    return text.split(' ')


def list2text(list):
    return ' '.join([word for word in list])


File_trash = open('trash.txt', 'r')
Trash = text2list(File_trash.read())

for post in Mposts.find():
    id = post.get("_id")
    text = post.get('text')
    if text == "" or text is None:
        continue

    text = formatting(text)
    l = text2list(text)
    l = [norm_word(word) for word in l]

    to_delete = []
    for index, word in enumerate(l):
        if trashpos(word) or norm_word(word) in Trash:
            to_delete.append(index)
            print(word.upper(), l)

    for index in sorted(to_delete, reverse=True):
        del l[index]

    text = del_spaces(list2text(l))
    Db.posts.update_one({"_id": id}, {"$set": {"formatted_text": text}})

File_trash.close()
