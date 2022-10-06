import requests
import json
from bs4 import BeautifulSoup
from kudago_event_parser import KudagoEventParser

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}


def save(data, file_name, encoding='utf-8'):
    with open(f'{file_name}.txt', 'w', encoding=encoding) as file:
        for item in data:
            file.write(f'{item}\n')


def load(file_name):
    data = []
    with open(f'{file_name}.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            data.append(line.strip())
    return data


def get_events_urls(url) -> set:
    events_urls = set()

    page = 1
    while True:
        response = requests.get(url=f'{url}?get_facets=1&page={page}', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        e_urls = soup.find_all('a', class_='post-title-link')

        for eu in e_urls:
            events_urls.add(eu.get('href'))

        if soup.find_all(class_='sorry-header'):
            break
        page += 1

    return events_urls


def get_events(event_urls):
    events = []
    for url in event_urls:
        event_parser = KudagoEventParser(url, headers)
        events.append(event_parser.get_event())
    return events


def main():
    url = 'https://kzn.kudago.com/events/'

    event_urls = get_events_urls(url)
    save(event_urls, 'event_urls')

    events = get_events(load('event_urls'))
    # events = get_events(['https://online.kudago.com/event/teatr-zarisovki-puteshestvij/'])
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(events, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
