import requests
from bs4 import BeautifulSoup
URL = 'https://finance.naver.com/item/sise_day.nhn?code=005930&page={page}'


def run():
    for i in range(1, 10):
        html = requests.get(URL.format(page=i)).text
        bs = BeautifulSoup(html)
        print()
