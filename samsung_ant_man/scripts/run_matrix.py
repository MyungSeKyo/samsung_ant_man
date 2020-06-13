from operator import itemgetter
import numpy as np
from dateutil import parser as date_parser
import urllib.request
from xml.dom import minidom
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from requests import get
from goose3 import Goose
import os
from stocks.models import WordProsCons,DailyStock
daily_updown = DailyStock.objects.all().orders_by("diff_yesterday")
daily_updown = daily_updown.values('date', 'diff_yesterday')

minval = abs(min(map(itemgetter('diff_yesterday'), daily_updown)))
maxval = abs(max(map(itemgetter('diff_yesterday'), daily_updown)))
if minval>maxval:
    daily_updown = [dict(d, diff_yesterday=(
        d['diff_yesterday'])/minval) for d in daily_updown]
else:
    daily_updown = [dict(d, diff_yesterday=(
        d['diff_yesterday'])/maxval) for d in daily_updown]


print(daily_updown)
text_dict = {}
days_text_list = []
for things in daily_updown:
    # dateconversion
    print(things['date'])
    LINK = "https://news.google.com/rss/search?q=samsung+electronics+when:" + \
        things['date']+"&hl=en-US&gl=US&ceid=US:en"

    xmldoc = minidom.parse(urllib.request.urlopen(LINK, timeout=2))
    itemlist = xmldoc.getElementsByTagName('item')
    today_text = ''
    # for newsitem in itemlist:
    doccount = 0
    for items in itemlist:
        if doccount > 0:
            break
        print(items)
        singlelink = items.getElementsByTagName('link')[0].firstChild.nodeValue
        pubdate = items.getElementsByTagName('pubDate')[0].firstChild.nodeValue
        date = date_parser.parse(pubdate).strftime("%Y%m%d")
        try:
            response = get(singlelink, timeout=10)
        except (urllib.exceptions.ReadTimeoutError, urllib.error.HTTPError):
            pass
        else:
            try:
                extractor = Goose()
                article = extractor.extract(raw_html=response.content)
                text_str = article.cleaned_text
                today_text += text_str
                doccount += 1
            except TypeError:
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
word_dist = []


for key, value in string_word, value_word:
    word_dist.append(WordProsCons(key, value))

WordProsCons.objects.bulk_create(word_dist)

