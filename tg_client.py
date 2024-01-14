from queue import Queue

from telethon.sync import TelegramClient

from config import TG_API_HASH, TG_API_ID, TG_CHANNEL_ID

queue = Queue()
client = TelegramClient("binance_watcher", TG_API_ID, TG_API_HASH)


def start_client():
    with client:
        while True:
            msg: str = queue.get()
            client.send_message(TG_CHANNEL_ID, msg)
