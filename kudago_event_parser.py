import re

import requests
from bs4 import BeautifulSoup


class KudagoEventParser:

    def __init__(self, event_url, headers):
        self.soup = self.__form_soup(event_url, headers)

    @staticmethod
    def __form_soup(url, headers):
        try:
            response = requests.get(url=url, headers=headers)
        except requests.exceptions.RequestException as ex:
            raise SystemExit(ex)
        soup = BeautifulSoup(response.text.replace("\xa0", " "), 'lxml')
        return soup

    def get_event(self):
        event = {}

        def soup_find_stripped_text(tag, **kwargs):
            result = self.soup.find(tag, **kwargs)
            if result is not None:
                result = result.text.strip()
            return result

        def get_event_schedule():
            schedule = self.soup.find('table', class_='post-big-details-schedule').find_all('td')
            schedule = " ".join([item.text.strip() for item in schedule])
            return " ".join(schedule.split())

        def get_event_source():
            source = self.soup.find('div', class_='post-big-details', id='additional-info')
            if source is not None:
                source = source.find('a')
            if source is not None:
                source = source.get('href')
            return source

        def get_event_images():
            images = self.soup.find_all("img", class_="post-big-preview-image")
            for i, img in enumerate(images):
                if img.get("src") is None:
                    images[i] = f'https://online.kudago.com/{img.get("data-src")}'
                else:
                    images[i] = f'https://online.kudago.com/{img.get("src")}'
            return images

        def remove_spaces_between_numbers(price):
            """Example: 8 000 -> 8000"""
            # return re.sub(r'(\d)\s+(\d)', r'\1\2', price) if not None else None
            return price


        event['title'] = soup_find_stripped_text('h1', class_='post-big-title')
        event['short_description'] = soup_find_stripped_text('div', id='item-description')
        event['full_desctiption'] = soup_find_stripped_text('div', id='item-description')
        event['schedule'] = get_event_schedule()
        event['price'] = remove_spaces_between_numbers(soup_find_stripped_text('span', id='event-price'))
        event['source'] = get_event_source()
        event['location'] = soup_find_stripped_text('span', class_='addressItem addressItem--single')
        event['views'] = soup_find_stripped_text('span', class_='post-views-number')
        event['images'] = get_event_images()
        return event
