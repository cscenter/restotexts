import base64
from pymongo import MongoClient
import os
import telethon
from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import JoinChannelRequest


print("Input your Telegram API id:")  # Authorisation
Api_id = int(input())
print("Input your API hash:")
Api_hash = str(input())

Resto = TelegramClient('session_name', Api_id, Api_hash)
Mclient = MongoClient('localhost', 27017)  # MongoDB should be already started

Db = Mclient.restotexts
Posts = Db.posts

Channels = {
            -1001141587803,  # Где вкусно поесть
            -1001100608817,  # Restoraids
            -1001164680315,  # FooDiscovery
            -1001122635434,  # Нерубинштейна
            -1001348529976,  # ПроКОФьевна
            -1001244221197,  # ЧИП ДИШ
            -1001163906641,  # Вкусный Питер
            -1001379894986,  # Непатрики
            -1001282209377,   # foodieguide
            -1001104433974   # Restinmsk
            }


async def main():

    await Resto.send_message('me', "start")
    total = 0
    e = 0

    for channel in Channels:
        await Resto(JoinChannelRequest(channel))

        async for message in Resto.iter_messages(channel):

            b64 = None

            if message.photo:

                try:
                    path = await message.download_media()
                    b64 = base64.encodebytes(open(path, "rb").read())
                    os.remove(path)

                except:  # sometimes there is trouble with profile pics
                    print()
                    print('=====OOPS!=====')
                    print(message.chat.title, ": ", message.date)
                    print('===============')
                    e += 1

            lat = None
            lng = None

            if message.geo:
                lat = message.geo.lat
                lng = message.geo.long

            tags = []
            links = []
            entities = message.get_entities_text()

            for ent, text in entities:

                if isinstance(ent, telethon.tl.types.MessageEntityHashtag):
                    s = text
                    tags.append(s)

                if isinstance(ent, telethon.tl.types.MessageEntityUrl):
                    s = text
                    links.append(s)

                if isinstance(ent, telethon.tl.types.MessageEntityTextUrl):
                    s = ent.url
                    links.append(s)

            post = {
                    "text": str(message.message),
                    "from": message.chat.id,
                    "message_id": message.id,
                    "title": str(message.chat.title),
                    "date": message.date,
                    "images": b64,
                    "tags": tags,
                    "links": links,
                    "category": None,
                    "address": {
                        "formatted_address": None,
                        "lat": lat,
                        "lng": lng,
                        "city": None
                        }

                    }
            Posts.insert_one(post)

        all_messages = await Resto.get_messages(channel)
        total += all_messages.total

    print("TOTAL: ", total)
    print("errors: ", e)
    await Resto.send_message('me', "finished")
    await Resto.send_message('me', total)
    await Resto.send_message('me', e)

with Resto:
    Resto.loop.run_until_complete(main())

