
import requests
import json

from tiktok_scraper import TiktokBot

service = "TIKTOK_BOT"
parameters = {
            "keywords":["beautiful destinations", "places to visit","places to travel", "places that don't feel real","travel hacks"],
            "hashtags": [
    "traveltok",
    "wanderlust",
    "backpackingadventures",
    "luxurytravel",
    "hiddengems",
    "solotravel",
    "roadtripvibes",
    "travelhacks",
    "foodietravel",
    "sustainabletravel"
]


        }

tiktok_bot = TiktokBot(
    parameters = parameters,
)
tiktok_bot.init_driver_local_chrome()

data = tiktok_bot.get_pages(service=service)
# print(data)

tiktok_bot.close()
tiktok_bot.quit()

