import urllib.request
from operator import itemgetter

import pandas as pd
from dateutil import parser as date_parser
from goose3 import Goose
from requests import get
from sklearn.feature_extraction.text import TfidfVectorizer
from xml.dom import minidom

# from stocks.models import WordProsCons, DailyStock
from stocks.models import DailyStock


def analyze_doc(doc):
    return [("단어", 0.5, 0.5),]


def analyze_word(word):
    return (0.5, 0.5)


def _build_matrix():
    daily_updown = DailyStock.objects.all().order_by("diff_yesterday")
    daily_updown = daily_updown.values('id', 'diff_yesterday')

    minval = abs(min(map(itemgetter('diff_yesterday'), daily_updown)))
    maxval = abs(max(map(itemgetter('diff_yesterday'), daily_updown)))
    if minval > maxval:
        daily_updown = [dict(d, diff_yesterday=(d['diff_yesterday']) / minval) for d in daily_updown]
    else:
        daily_updown = [dict(d, diff_yesterday=(d['diff_yesterday']) / maxval) for d in daily_updown]

    text_dict = {}
    days_text_list = []
    for things in daily_updown:
        # dateconversion
        things['id'] = str(things['id'])
        print(things['id'])
        LINK = 'https://news.google.com/rss/search?q=samsung+electronics+when:{}-{}-{}&hl=en-US&gl=US&ceid=US:en'.format(
            things['id'][:4],
            things['id'][4:6],
            things['id'][6:],
        )
        print(LINK)
        xmldoc = minidom.parse(urllib.request.urlopen(LINK, timeout=10))
        itemlist = xmldoc.getElementsByTagName('item')
        today_text = ''
        # for newsitem in itemlist:
        doccount = 0
        for items in itemlist:
            if doccount > 10:
                break
            print(items)
            singlelink = items.getElementsByTagName('link')[0].firstChild.nodeValue
            pubdate = items.getElementsByTagName('pubDate')[0].firstChild.nodeValue
            date = date_parser.parse(pubdate).strftime("%Y%m%d")
            try:
                response = get(singlelink, timeout=10)
            except Exception as e:
                print('here')
                pass
            else:
                try:
                    extractor = Goose()
                    article = extractor.extract(raw_html=response.content)
                    text_str = article.cleaned_text
                    today_text += text_str
                    doccount += 1
                except TypeError:
                    print('this')
                    pass
        days_text_list.append(today_text)

    scripts = days_text_list
    len(days_text_list)
    vectorizer = TfidfVectorizer(
        stop_words='english', token_pattern=r'(?u)\b[A-Za-z]+\b')
    bag_of_words = vectorizer.fit_transform(scripts)
    value_word = pd.DataFrame(bag_of_words.toarray()).mul(
        list(map(lambda d: d['diff_yesterday'], daily_updown)), axis=0).sum(axis=0)
    string_word = vectorizer.get_feature_names()
    return {string_word[i]: value_word[i] for i in range(len(string_word))}
