from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import JoinChannelRequest
import telethon
from pymongo import MongoClient
import base64
import os

print("Input your Telegram API id:")  # Authorisation
api_id = int(input())
print("Input your API hash:")
api_hash = str(input())

resto = TelegramClient('session_name', api_id, api_hash)
mclient = MongoClient('localhost', 27017)  # MongoDB should be already started

db = mclient.restotexts
posts = db.posts

channels = {
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

    await resto.send_message('me', "start")
    total = 0
    e = 0

    for channel in channels:
        await resto(JoinChannelRequest(channel))

        async for message in resto.iter_messages(channel):

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
                    pass

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
            posts.insert_one(post)

        all_messages = await resto.get_messages(channel)
        total += all_messages.total

    print("TOTAL: ", total)
    print("errors: ", e)
    await resto.send_message('me', "finished")
    await resto.send_message('me', total)
    await resto.send_message('me', e)

with resto:
    resto.loop.run_until_complete(main())

