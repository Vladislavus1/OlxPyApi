import requests
from bs4 import BeautifulSoup
from exceptions import *
from concurrent.futures import ThreadPoolExecutor, as_completed

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def get_soup(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup, response.status_code


def get_allowed_urls():
    base_urls = ["https://www.olx.ua", "https://www.olx.pl", "https://www.olx.kz"]
    allowed_urls = []
    for base_url in base_urls:
        bs4_soup, _ = get_soup(base_url)
        categories_urls = bs4_soup.select("[data-testid='home-categories-menu'] a")
        for categories_url in categories_urls:
            url = f"{base_url}/{categories_url['href'].split('/')[1]}" if base_url != "https://www.olx.ua" else f"{base_url}/{categories_url['href'].split('/')[1]}/{categories_url['href'].split('/')[2]}"
            if base_url in url and url != f"{base_url}/":
                allowed_urls.append(url)
        allowed_urls.append(
            "https://www.olx.pl/oferty/q-" if base_url == "https://www.olx.pl"
            else "https://www.olx.kz/list/q-" if base_url == "https://www.olx.kz"
            else "https://www.olx.ua/uk/list/q-"
        )
    return allowed_urls


class OlxAd:
    def __init__(self, title, price, url, images):
        self.title = title
        self.price = price
        self.url = url
        self.images = images


class OlxParser:
    def __init__(self, logging):
        self.logging = logging
        self.retries = 0
        self.max_retries = 1
        self.logs = []

    def get_products(self, url):
        base_url = f"{url.split('/')[0]}//{url.split('/')[2]}"
        ad_urls = []
        ads = []
        allowed_urls = get_allowed_urls()

        if url.startswith(tuple(allowed_urls)):
            try:
                def get_ads(bs4_soup):
                    nonlocal ad_urls
                    l_cards = bs4_soup.select("[data-testid='l-card']")
                    for l_card in l_cards:
                        h6 = l_card.find('h6')
                        href = l_card.find('a')
                        product_url = f"{base_url}{href['href']}"
                        product_price = l_card.select_one("[data-testid='ad-price']")
                        product_price = product_price.text if product_price else None
                        product_title = h6.text
                        if product_url.startswith(
                                ("https://www.olx.pl/d/oferta", "https://www.olx.ua/d/uk/obyavlenie",
                                 "https://www.olx.kz/d/obyavlenie")
                        ):
                            ad_urls.append(
                                OlxAd(title=product_title, price=product_price, url=product_url, images=None))
                    if self.logging:
                        print(" (done)")

                def get_ad_info(product):
                    nonlocal ads
                    bs4_soup, bs4_response_code = get_soup(product.url)
                    if self.logging:
                        print("  •", product.url, end="")
                    if bs4_response_code != 200:
                        if self.logging:
                            print(" (aborted)")
                    else:
                        ad_inactive_msg = bs4_soup.select("[data-testid='ad-inactive-msg']")
                        if len(ad_inactive_msg) != 0:
                            print(" (aborted)")
                        else:
                            print(f" (response code: {bs4_response_code})", end="")
                            images = bs4_soup.select("[data-testid='ad-photo'] img")
                            product_images = [image['src'] for image in images]
                            if images:
                                product.images = product_images
                            ads.append(product)
                            if self.logging:
                                print(" (done)")

                soup, response_code = get_soup(url)
                total_count = soup.select_one("[data-testid='listing-count-msg']").text
                if int([element for element in total_count.split() if element.isdigit()][0]) != 0:
                    pagination_list = soup.select_one("[data-testid='pagination-list']")
                    if pagination_list is None:
                        if self.logging:
                            print(f"Parsing {url}", end="")
                        if self.logging:
                            print(f" (response code: {response_code})", end="")
                        get_ads(soup)
                    else:
                        pagination_items = pagination_list.select("[data-testid='pagination-list-item']")
                        max_page = int(pagination_items[-1].text)
                        url_split = url.split("/")
                        url += "&page=" if url_split[-1] != '' else "?page="

                        with ThreadPoolExecutor(max_workers=5) as executor:
                            futures = {executor.submit(get_soup, f"{url}{page_index + 1}"): page_index for page_index in
                                       range(max_page)}
                            for future in as_completed(futures):
                                soup, response_code = future.result()
                                if self.logging:
                                    print(f"Parsing {url + str(futures[future] + 1)} (response code: {response_code})",
                                          end="")
                                get_ads(soup)

                    if self.logging:
                        print("\nGetting information:")
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        futures = {executor.submit(get_ad_info, ad): ad for ad in ad_urls}
                        for future in as_completed(futures):
                            try:
                                future.result()
                            except requests.RequestException:
                                try:
                                    future.result()
                                except requests.RequestException:
                                    print(" (aborted)")
                    return ads
                else:
                    raise NoResultFoundError(url)
            except NoResultFoundError:
                raise
            except Exception as e:
                if self.retries <= self.max_retries:
                    self.retries += 1
                    self.logs.append(str(e))
                    if self.logging:
                        print(f"\nParsing was interrupted due to error, restarting! (retry attempt: {self.retries})")
                    self.get_products(url)
                else:
                    with open("error_logs.txt", "w", encoding="utf-8") as log:
                        for log_row in self.logs:
                            log.write(log_row + "\n")
                    raise MaxAttemptsReached()
        else:
            raise NotOlxUrlError(url)