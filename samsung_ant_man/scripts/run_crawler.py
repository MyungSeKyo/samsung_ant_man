import requests
from bs4 import BeautifulSoup
from stocks.models import DailyStock


URL = 'https://finance.naver.com/item/sise_day.nhn?code=005930&page={page}'


def run():
    DailyStock.objects.all().delete()

    for i in range(1, 100):
        html = requests.get(URL.format(page=i)).text
        bs = BeautifulSoup(html, "html.parser")
        valid_num = [2, 3, 4, 5, 6, 10, 11, 12, 13, 14]

        for num in valid_num:
            day = list(bs.find_all('tr')[num])[1].text.replace(".", "", 2)
            end_p = int(list(bs.find_all('tr')[num])[3].text.replace(",", ""))
            diff = int(list(bs.find_all('tr')[num])[5].text.strip().replace(",", ""))
            current_p = int(list(bs.find_all('tr')[num])[7].text.replace(",", ""))
            high_p = int(list(bs.find_all('tr')[num])[9].text.replace(",", ""))
            row_p = int(list(bs.find_all('tr')[num])[11].text.replace(",", ""))
            vol = int(list(bs.find_all('tr')[num])[13].text.replace(",", ""))

            if diff == 0 or 'up' in str(list(bs.find_all('tr')[num])[5].find('img')):
                pass
            elif 'down' in str(list(bs.find_all('tr')[num])[5].find('img')):
                diff = -1 * diff

            if current_p > 1000000:
                end_p //= 50
                diff //= 50
                current_p //= 50
                high_p //= 50
                row_p //= 50
                vol //= 50

            DailyStock.objects.get_or_create(
                end_price=end_p, diff_yesterday=diff, current_price=current_p, high_price=high_p,
                row_price=row_p, volume=vol, year=day[:4], month=day[4:6], date=day[6:], index_in_page=num
            )
        print('completed page#{}'.format(i))
