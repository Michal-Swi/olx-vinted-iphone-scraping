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
        channel_id = int(open('DISCORD_CHANNEL_ID').read())
    except Exception as e:
        print(e)

    await main_functionality(channel_id)


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
        driver.quit()
        return
    finally:
        driver.quit()

    final_offers = []
    for offer in offers:
        if not scraper.is_desired_iphone(offer['title'], offer['added_time']):
            print('Unused: ' + str(offer) + '\n')
            continue
        print(str(offer) + '\n')
        final_offers.append(offer)
    return final_offers


async def clear_used_offers(used_offers):
    offers_len = len(used_offers)

    if offers_len <= 10:
        return used_offers

    i = offers_len - 10

    new_offers = []
    while i < offers_len:
        new_offers.append(used_offers[i])
        i += 1

    return new_offers


async def main_functionality(channel_id):
    print('Entered main functionality')

    channel = client.get_channel(channel_id)

    # await channel.send('Scraping')

    left = 8
    right = 12

    scrapes_run = 0

    already_used_offers = []
    while not client.is_closed():
        start_time = time.time()
        rand = random.randrange(left, right)
        print('Sleeping for ' + str(rand))

        try:
            offers = bot_scrape()
        except Exception as e:
            print(str(e))
            continue

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
                'Ogłoszenie dodano: ' + f"{offer['added_time']}\n"
            )

            print(offer['image_url'])

            if offer['image_url'] is not None:
                try:
                    new_embed.image.url = offer['image_url']
                    new_embed.set_image(url=offer['image_url'])
                except Exception as e:
                    print(e)

            await channel.send(embed=new_embed)
            await asyncio.sleep(2)

            already_used_offers.append(offer['title'])

            scrapes_run += 1

            if scrapes_run >= 1000:
                already_used_offers = clear_used_offers(already_used_offers)

        print('\n')
        print('\n')
        print('\n')

        await asyncio.sleep(rand)
        print(time.time() - start_time)

        log_file = open('log_file', 'a')
        log_file.write(str(time.time() - start_time))
        log_file.write('\n')
        log_file.close()

DISCORD_API_KEY = open("DISCORD_API_KEY", "r")
DISCORD_API_KEY = DISCORD_API_KEY.read()

client.run(DISCORD_API_KEY)
