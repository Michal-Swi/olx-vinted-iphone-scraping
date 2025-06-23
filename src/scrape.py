import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from urllib.parse import urljoin

olx_url = open('BASE_OLX_URL').read()
olx_div = "div[data-cy='l-card']"
vinted_div = "div[data-testid='grid-item']"
vinted_url = open('BASE_VINTED_URL').read()


class Scraper:
    def is_desired_iphone(self, offer_title, time_added):
        desired_phones = ['x', 'xs', 'xr', '11',
                          '11', '12', '13', '14', '15', '16', 'se']
        offer_name = str(offer_title)
        offer_name = offer_name.lower()

        time_added_lower = str(time_added)
        time_added_lower = time_added_lower.lower()

        # Throwing out old offers
        if 'dzisiaj' not in time_added_lower:
            return False

        if 'odświeżono' in time_added_lower:
            return False

        if 'bateria' in offer_title:
            return False

        proboably_not_phones = ['etui', 'szkło',
                                'szklo', 'ladowarka', 'ładowarka']

        # Throwing out non-phones
        for red_flag in proboably_not_phones:
            if red_flag in offer_name:
                print("Unused: " + offer_name)
                return False

        try:
            split_offer_name = offer_name.split(' ')
        except Exception as e:
            print(e)

        flag = False
        for word in split_offer_name:
            if flag and word in desired_phones:
                return True
            elif flag and word not in desired_phones:
                return False

            if word == 'iphone':
                flag = True

        return False

    def setup_driver(self):
        # proxy = self.get_random_proxy()

        profile = FirefoxProfile()

        # values = proxy.split(':')
        # ip = values[0]
        # port = values[1]

        # print(ip + ' ' + port)

        # profile.set_preference("network.proxy.type", 1)
        # profile.set_preference("network.proxy.http", ip)
        # profile.set_preference("network.proxy.http_port", int(port))
        # profile.set_preference("network.proxy.ssl", ip)
        # profile.set_preference("network.proxy.ssl_port", int(port))
        # profile.set_preference("network.proxy.socks_remote_dns", True)
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        # profile.set_preference("permissions.default.stylesheet", 2)
        # profile.set_preference("permissions.default.image", 2)
        # profile.set_preference("javascript.enabled", False)
        profile.update_preferences()

        options = Options()
        options.headless = True
        options.profile = profile
        options.add_argument('--private')
        # options.add_argument('--headless')

        driver = webdriver.Firefox(options=options)
        # driver.get("https://whatismyipaddress.com")

        # options = uc.ChromeOptions()

        # driver = uc.Chrome(use_subprocess=False)
        # try:
        #    driver.get(BASE_URL)
        # except Exception as e:
        #    print('Driver connection error ' + str(e))

        return driver

    def open_site(self, driver, url):
        try:
            driver.get(url)
        except Exception as e:
            print(e)
            return None

        return driver

    def accept_cookies(self, driver):
        try:
            accept = WebDriverWait(driver, 7).until(
                EC.element_to_be_clickable(
                    (By.ID, 'onetrust-accept-btn-handler'))
            )
            accept.click()
            print("Popup closed")
        except Exception:
            print('No popup')

    def wait_for_offers(self, driver, div):
        print('Waiting for offers')
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, div))
        )
        print('Offers ready')

    def extract_olx_offer_data(self, card):
        try:
            link_elem = card.find_element(By.TAG_NAME, "a")
            href = link_elem.get_attribute("href")
            full_url = urljoin(olx_url, href)

            try:
                title_elem = card.find_element(By.TAG_NAME, "h6")
            except Exception:
                title_elem = card.find_element(By.TAG_NAME, "h4")

            title = title_elem.text.strip()

            try:
                img_elem = card.find_element(By.TAG_NAME, "img")

                img_url = (
                    img_elem.get_attribute("data-src")
                    or img_elem.get_attribute("data-imgsrc")
                    or img_elem.get_attribute("src")
                )

                if "no_thumbnail" in img_url or "nophoto" in img_url:
                    img_url = None
            except Exception:
                img_url = None

            try:
                price_elem = card.find_element(
                    By.CSS_SELECTOR, "p[data-testid='ad-price']")
                price = price_elem.text.strip()
            except Exception:
                price = "N/A"

            try:
                location_time_elem = card.find_element(
                    By.CSS_SELECTOR, "p[data-testid='location-date']")
                location_time_text = location_time_elem.text.strip()

                if " - " in location_time_text:
                    location, added_time = location_time_text.split(" - ", 1)
                else:
                    location = location_time_text
                    added_time = "Brak danych"
            except Exception as e:
                print(e)
                location = "Brak"
                added_time = "Brak"

            try:
                shipping_elem = card.find_element(
                    By.CSS_SELECTOR, "svg[aria-label='Dostawa OLX']")
                shipping_available = True
            except Exception:
                shipping_available = False

            return {
                "title": title,
                "price": price,
                "url": full_url,
                "location": location,
                "shipping": shipping_available,
                "added_time": added_time,
                "image_url": img_url
            }

        except Exception as e:
            print(f"Skipping one card due to error: {e}")
            return None

    def extract_vinted_offer_data(self, card):
        link_elem = card.find_element(By.TAG_NAME, "p")

    def scrape_offers(self, driver, div, max_offers=10):
        print('Scraping offers')
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, div)
        except Exception:
            return None

        results = []
        for card in cards[:max_offers]:
            print(card)
            # data = self.extract_offer_data(card)
            data = self.extract_vinted_offer_data(card)
            if data:
                results.append(data)
        return results


def bot_scrape():
    scraper = Scraper()
    driver = scraper.setup_driver()

    driver = scraper.open_site(driver, vinted_url)

    if driver is None:
        print('Site did not open')
        return

    time.sleep(2)

    try:
        scraper.accept_cookies(driver)
        scraper.wait_for_offers(driver, vinted_div)
        offers = scraper.scrape_offers(driver, vinted_div)
        print(offers)
    except Exception as e:
        print(str(e) + ' \nQuitting')
        exit(-1)
    finally:
        driver.quit()

    return

    print(offers)

    final_offers = []
    for offer in offers:
        print(str(offer) + '\n')
        if not scraper.is_desired_iphone(offer, None):
            continue
        final_offers.append(offer)

    print('\n' + '\n')
    print('\n' + '\n')

    return final_offers


bot_scrape()
