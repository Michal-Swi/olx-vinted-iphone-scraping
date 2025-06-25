import discord
import random
import time
from scrape import Scraper
import asyncio
import datetime

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

try:
    channel_id = int(open('DISCORD_CHANNEL_ID').read())
except Exception as e:
    print(e)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    await main_functionality()

_id = int(open('ID', 'r').read())
stop_message = open('STOP_MESSAGE', 'r').read()
stop_user_message = open('STOP_USER_MESSAGE', 'r').read()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel = client.get_channel(channel_id)

    await channel.send(str(message.author.name) + ' ' + str(message.content))

    if message.author.id == _id and message.content == stop_message:
        await channel.send(stop_user_message)
        exit(-1)


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

    print(offers)

    final_offers = []
    for offer in offers:
        if not scraper.is_desired_iphone(offer['title'], offer['added_time']):
            # print('Unused: ' + str(offer) + '\n')
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


vinted_url = open('BASE_VINTED_URL', 'r').read()


def scrape_vinted():
    try:
        scraper = Scraper()
        driver = scraper.setup_driver()
        offers = scraper.scrape_vinted_offers(driver, vinted_url)
    except Exception:
        driver.quit()
        return None
    finally:
        driver.quit()

    final_offers = []
    for offer in offers:
        if not scraper.is_desired_iphone(offer['title'], 'dzisiaj'):
            # print('Unused: ' + str(offer) + '\n')
            continue
        # print(str(offer) + '\n')
        final_offers.append(offer)
    return final_offers


olx_div = "div[data-cy='l-card']"
olx_url = open('BASE_OLX_URL').read()


def scrape_olx():
    try:
        scraper = Scraper()
        driver = scraper.setup_driver()
        scraper.open_site(driver, olx_url)
        scraper.accept_cookies(driver)
        scraper.wait_for_offers(driver, olx_div)
        offers = scraper.scrape_offers(driver, olx_div)
    except Exception as e:
        print('Scrape olx error ' + str(e))
        driver.quit()
        return None
    finally:
        driver.quit()

    final_offers = []
    for offer in offers:
        if not scraper.is_desired_iphone(offer['title'], offer['added_time']):
            # print('Unused: ' + str(offer) + '\n')
            continue
        # print(str(offer) + '\n')
        final_offers.append(offer)
    return final_offers


def get_time_needed(base_time):
    now = str(datetime.datetime.now())
    now = now.split(' ')

    first = int(now[1][0])

    if first > 2:
        return base_time + 20

    second = int(now[1][1])

    if first == 0 and second < 6:
        return base_time + 20

    return base_time


async def main_functionality():
    print('Entered main functionality')

    channel = client.get_channel(channel_id)

    # await channel.send('Scraping')

    scrapes_run_olx = 0
    scrapes_run_vinted = 0

    already_used_offers_olx = []
    already_used_offers_vinted = []
    while not client.is_closed():
        left = get_time_needed(8)
        right = get_time_needed(12)

        start_time = time.time()
        rand = random.randrange(left, right)
        print('Sleeping for ' + str(rand))

        offers_olx = None

        try:
            offers_olx = scrape_olx()
        except Exception as e:
            print('Olx scraping error ' + str(e))
            offers_olx = None

        offers_vinted = None

        try:
            # offers_vinted = scrape_vinted()
            pass
        except Exception as e:
            print('Vintes scraping error ' + str(e))
            offers_vinted = None

        if offers_olx is not None:
            for offer in offers_olx:
                if offer['title'] in already_used_offers_olx:
                    continue

                print(offer['title'])

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
                await asyncio.sleep(1)

                already_used_offers_olx.append(offer['title'])

                scrapes_run_olx += 1

                if scrapes_run_olx >= 1000:
                    already_used_offers_olx = clear_used_offers(
                        already_used_offers_olx)
                    scrapes_run_olx = 0

        if offers_vinted is not None:
            for offer in offers_vinted:
                if offer['title'] in already_used_offers_vinted:
                    continue

                new_embed = discord.Embed()
                new_embed.title = 'Nowa oferta'
                new_embed.description = (
                    'Tytuł: ' + f"{offer['title']}\n" +
                    'Cena: ' + f"{offer['price']}\n" +
                    'Link: ' + f"{offer['url']}\n"
                )

                print(offer['image'])

                if offer['image'] is not None:
                    try:
                        new_embed.image.url = offer['image']
                        new_embed.set_image(url=offer['image'])
                    except Exception as e:
                        print(e)

                await channel.send(embed=new_embed)
                await asyncio.sleep(1)

                already_used_offers_vinted.append(offer['title'])

                scrapes_run_vinted += 1

                if scrapes_run_vinted >= 1000:
                    already_used_offers_vinted = clear_used_offers(
                        already_used_offers_vinted)
                    scrapes_run_vinted = 0

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

try:
    client.run(DISCORD_API_KEY)
except Exception as e:
    print(e)
