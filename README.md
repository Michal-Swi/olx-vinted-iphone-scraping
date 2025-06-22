# Scraper Dev Docs
This file is supposed to help myself and future contributors undesteand the mess of a codebase I am creating.\
This project has a lot hardcoded but it's temporary, in its final form the project is supposed to scrape offers from 
various shopping sites every 8-10 seconds with customizable filters and sorts. 

## How Does Scraper Work
Scraper() is the base class that scrapes offers from various shopping websites (currently only olx.pl).\

### scrape.py variables and methods
**BASE_URL** - the URL from which the Scraper class will scrape offers. BASE_URL is read from 'BASE_URL' file.\ 
**proxies** - self-explenatory. All proxies are read from 'proxies' file.\
**bot_scrape()** - method that can creates Scraper, calls all needed methods, handles errors and prints desired offers. 
bot_scrape() in scrape.py is a test version of bot_scrape() in bot.py file\
[!NOTE]
Desired offers are offers that returned True from Scraper.is_desired_phone() method, this will be changed!\

### Scraper Methods
**setup_driver()** - handles all webdriver options including proxies, opens the site from BASE_URL variable and returns
the webdriver. 
**get_random_proxy()** - returns random proxy from the 'proxies' files, used in setup_driver().
**accept_cookies(driver)** - accepts cookies by searching for 'Akceptuję' button.
**wait_for_offers(driver)** - waits for offers, because they might take a while to load.
**scrape_offers(driver, max_offers=10)** - searches for wanted divs on site and returns extracted offers.
**extract_offer_data(card)** - extracts wanted data from card (div) and returns it.
**is_desired_iphone(offer_title, time_added)** - method for checking some hardcoded conditions, will be deleted. 

## How does the bot work
bot essentialy just uses Scraper() every 11-16 seconds (will be changed).\

### bot.py variables and method
**bot_scrape()** - this method in bot.py is superior, production version of bot_scrape() from scrape.py.
**main_functionality(channel_id)** - asynchronus function that as long as client is active, every 11-16 seconds 
scrapes for some new offers and sends them to channel_id as an embed. This function uses asyncio, but does so poorly. 
main_functionality() remembers already seen offers in already_used_offers array
**channel_id** - variable taken from 'DISCORD_CHANNEL_ID' file
**DISCORD_API_KEY** - discord api key taken from 'DISCORD_API_KEY' file
