import discord
import random
import time
from scrape import Scraper
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    try:
        channel_id = open('DISCORD_CHANNEL_ID').read()
    except Exception as e:
        print(e)

    client.loop.create_task(main_functionality(channel_id))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

    if message.content == 'hello':
        await message.channel.send('siema')


def bot_scrape():
    scraper = Scraper()
    driver = scraper.setup_driver()
    time.sleep(2)

    try:
        scraper.accept_cookies(driver)
        scraper.wait_for_offers(driver)
        offers = scraper.scrape_offers(driver)
    except Exception as e:
        print(str(e) + ' \nQuitting')
        exit(-1)
    finally:
        driver.quit()

    final_offers = []
    for offer in offers:
        if not scraper.is_desired_iphone(offer['title']):
            print('Unused: ' + str(offer) + '\n')
            continue
        print(str(offer) + '\n')
        final_offers.append(offer)
    return final_offers


async def main_functionality(channel_id):
    print('Entered main functionality')

    channel = client.get_channel(channel_id)

    left = 11
    right = 16

    already_used_offers = []
    while not client.is_closed():
        rand = random.randrange(left, right)
        print('Sleeping for ' + str(rand))

        try:
            loop = asyncio.get_event_loop()
            offers = await loop.run_in_executor(None, bot_scrape)
        except Exception as e:
            print(str(e))

        for offer in offers:
            if offer['title'] in already_used_offers:
                continue

            new_embed = discord.Embed()
            new_embed.title = 'Nowa oferta'
            new_embed.description = (
                'Tytuł: ' + f"{offer['title']}\n" +
                'Cena: ' + f"{offer['price']}\n" +
                'Lokalizacja: ' + f"{offer['location']}\n" +
                'Link: ' + f"{offer['url']}\n" +
                'Ogłoszenie dodano: ' + f"{offer['added_time']}"
            )

            await channel.send(embed=new_embed)
            await asyncio.sleep(2)

            already_used_offers.append(offer['title'])

        print('\n')
        print('\n')
        print('\n')

        await asyncio.sleep(rand)

DISCORD_API_KEY = open("DISCORD_API_KEY", "r")
DISCORD_API_KEY = DISCORD_API_KEY.read()

client.run(DISCORD_API_KEY)
