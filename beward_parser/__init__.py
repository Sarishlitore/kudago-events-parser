from csv import DictWriter

import app

import requests
from bs4 import BeautifulSoup

from fstream.file import save, load


class BewardParser:
    def __init__(self, headers):
        self.__headers = headers

    def __form_soup(self, url):
        try:
            response = requests.get(url=url, headers=self.__headers)
        except requests.exceptions.RequestException as ex:
            raise SystemExit(ex)
        return BeautifulSoup(response.content, 'lxml')

    def __collect_products_urls(self, url):
        category_page_soup = self.__form_soup(url=url)
        p_urls = category_page_soup.find_all('td', class_='model')[1:]
        for it, tag in enumerate(p_urls):
            p_urls[it] = tag.div.table.tbody.tr.td.a.get('href')
        return p_urls

    def __collect_products_urls_from_category(self, category_url):
        catalog_page_soup = self.__form_soup(url=category_url)
        sub_categories_urls = catalog_page_soup.find('ul', class_='sub-menu').find_all('a')
        pr_urls = []
        for sub_cat_url in sub_categories_urls:
            pr_urls.extend(self.__collect_products_urls(sub_cat_url.get('href')))
        return pr_urls

    def collect_products_urls_from_catalog(self):
        soup = self.__form_soup(url='https://www.beward.ru/katalog/')
        categories_urls = soup.find('div', class_='left-nav').find_all('a')[:-3]
        products_urls = []

        for cat_url in categories_urls:
            try:
                products_urls.extend(self.__collect_products_urls_from_category(cat_url.get('href')))
            except Exception as ex:
                print(ex, cat_url)
        return products_urls

    def collect_product_data(self, product_url):
        def none_on_failure(f):
            def applicator(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except:
                    print('Error')
                    return None

            return applicator

        @none_on_failure
        def collect_article():
            article = soup.find('div', id='breadcrumbs').find_all('span')[-1].text
            return article

        @none_on_failure
        def collect_ie_name():
            ie_name = soup.find('h1', id='heading').text
            return ie_name

        @none_on_failure
        def collect_announcement():
            announcement = soup.find('tr', class_='note').td.p.text
            return announcement

        @none_on_failure
        def collect_ie_preview_picture():
            ie_preview_picture = soup.find('div', class_='image').img.get('src')
            return ie_preview_picture

        @none_on_failure
        def collect_icat_price1_price():
            icat_price1_price = soup.find('tr', class_='price').find('td').text
            return icat_price1_price

        @none_on_failure
        def collect_more_photos():
            photos_soup = self.__form_soup(f'{product_url}#gallery')
            tags = photos_soup.find('ul', class_='images').find_all('a')
            more_photos = [tag.get('href') for tag in tags]
            return more_photos

        @none_on_failure
        def collect_downloads():
            downloads_soup = self.__form_soup(f'{product_url}#files')
            tags = downloads_soup.find_all('td', class_='download')
            downloads = [tag.a.get('href') for tag in tags[1:]]
            return downloads

        soup = self.__form_soup(product_url)
        product = {'article': collect_article(),
                   'ie_name': collect_ie_name(),
                   'announcement': collect_announcement(),
                   'ie_preview_picture': collect_ie_preview_picture(),
                   'icat_price1_price': collect_icat_price1_price(),
                   'more_photos': collect_more_photos(),
                   'downloads': collect_downloads()}
        return product


def main():
    beward_parser = BewardParser(headers=app.headers)

    # save(beward_parser.collect_products_urls_from_catalog(), 'product_urls')

    product_urls = load('product_urls')
    keys_list = list(beward_parser.collect_product_data(product_urls[0]).keys())
    products = []

    c = 0
    for url in product_urls:
        products.append(beward_parser.collect_product_data(url))
        c += 1
        if c == 20:
            break
    with open('spreadsheet.csv', 'w', encoding='utf-8', newline='') as outlife:
        writer = DictWriter(outlife, keys_list)
        writer.writeheader()
        writer.writerows(products)


if __name__ == '__main__':
    main()
