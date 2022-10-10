import re

import requests
from bs4 import BeautifulSoup

import app
from fstream import file


class CollectomaniaVinylParser:
    def __init__(self, headers):
        self.__vinyls = []
        self.__vinyls_urls = []
        self.__headers = headers

    def __collect_vinyl_urls(self):
        page = 1
        while True:
            soup = self.__form_soup(url=f'https://collectomania.ru/collection/vinil?page={page}',
                                    headers=self.__headers)
            e_urls = soup.find_all('div', class_='product-preview__title')
            for eu in e_urls:
                self.__vinyls_urls.append(f'https://collectomania.ru{eu.a.get("href")}')
            print(f'{page}/459')
            if soup.find_all(class_='empty-catalog-message'):
                break
            page += 1

    @staticmethod
    def __form_soup(url, headers):
        try:
            response = requests.get(url=url, headers=headers)
        except requests.exceptions.RequestException as ex:
            raise SystemExit(ex)
        return BeautifulSoup(response.text, 'lxml')

    def __collect_vinyl_data(self, url):
        def find_state():
            state = soup.find('span', string=re.compile('Состояние'))
            if state is not None:
                state = state.findNext('span').next.text.strip()
            return state

        def find_span(string):
            tag = soup.find('span', string=re.compile(string))
            if tag is not None:
                tag = tag.findNext('span')
            if tag is not None:
                tag = " ".join(tag.text.split())
            return tag

        def find_publication_date():
            date = soup.find('span', string=re.compile('Год издания'))
            if date is None:
                date = soup.find('span', string=re.compile('Год выпуска'))
            return date.findNext('span').text.strip()

        vinyl = {}
        soup = self.__form_soup(url, self.__headers)
        vinyl['title'] = soup.find('h1', class_='product__title heading').text.strip()
        vinyl['state'] = find_state()
        vinyl['performer'] = find_span('Исполнитель')
        vinyl['label'] = find_span('Лейбл')
        vinyl['genres'] = find_span('Жанры')
        vinyl['sound'] = find_span('Звучание')
        vinyl['publication_date'] = find_publication_date()
        vinyl['country_of_production'] = find_span('Страна производства')
        vinyl['package'] = find_span('Упаковка')
        return vinyl

    def __collect_vinyls(self):
        for vu in self.__vinyls_urls:
            try:
                self.__vinyls.append(self.__collect_vinyl_data(vu))
            except Exception as ex:
                print(ex, vu)

    def parse(self):
        self.__collect_vinyl_urls()
        self.__collect_vinyls()

    def get_vinyls(self):
        return self.__vinyls


def main():
    coll_parser = CollectomaniaVinylParser(app.headers)
    coll_parser.parse()
    file.json_dump(coll_parser.get_vinyls(), 'vinyls')


if __name__ == '__main__':
    main()
