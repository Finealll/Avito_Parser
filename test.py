import requests
from bs4 import BeautifulSoup
import csv
import os

URL = 'https://www.avito.ru/rossiya'
HEADERS = {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
           'accept': '*/*'}
FILE = 'items.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_context(html):
    soup = BeautifulSoup(html, 'html.parser')
    snippet_list = soup.find_all('div', class_='item__line')
    snippets = []
    for item in snippet_list:
        snippets.append({
            'title': item.find('a', class_='snippet-link').text,
            'cost': item.find('span', class_='snippet-price').text.replace('\n', '').replace('  ', ' ').strip().encode('ascii', errors='ignore').decode(),
            'city': item.find('span', class_='item-address__string').text.replace('\n', '').strip(),
            'date': item.find('div', class_='snippet-date-info').get('data-tooltip') if item.find('div', class_='snippet-date-info').get('data-tooltip') != '' else '-',
            'photo_link': item.find('img', class_='large-picture-img').get('src') if item.find('img', class_="large-picture-img") is not None else '-',
            'href': URL + item.find('a', class_='snippet-link').get('href'),
        })
    return snippets


def save_file(items, patch):        #Сохраняем в файл
    with open(patch, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Цена', 'Город', 'Дата размещения', 'Ссылка на фото', 'Ссылка на страницу'])
        for item in items:
            writer.writerow([item['title'], item['cost'], item['city'], item['date'], item['photo_link'], item['href']])


def captcha(html): #Что то тут надо сделать с капчой
    print("Капча!")


def parse(question):
    question = question.strip().replace('', '+')
    html = get_html(URL, {'q': question})
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        # print(soup)
        pagination_info = soup.find_all('span', class_='pagination-item-1WyVp')
        # print(pagination_info)
        number_of_pages = int(pagination_info[-2].text)
        items = []
        for number in range(1, number_of_pages+1):
            print(f"Парсинг страницы {number} из {number_of_pages}")
            html = get_html(URL, {'q': question, 'p': number})
            if html.status_code == 429:
                captcha(html)
            else:
                items.extend(get_context(html.text))
        print('Сохраняю...')
        save_file(items, FILE)
        os.startfile(FILE)     #Для сия import os
    elif html.status_code == 404:
        print('Отсутствуют товары по данному запросу!')
    elif html.status_code == 429:
        captcha(html)
    else:
        print('Сайт не был открыт')


def main():
    print('Введите запрос:')
    question = input()
    parse(question)

if __name__ == "__main__":
    main()
