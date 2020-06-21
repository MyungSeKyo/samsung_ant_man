import pickle
import urllib.request
from operator import itemgetter
from xml.dom import minidom

import pandas as pd
from dateutil import parser as date_parser
from goose3 import Goose
from requests import get
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from django.conf import settings
# from stocks.models import WordProsCons, DailyStock
from stocks.models import DailyStock, DailyDocument


def analyze_doc(doc):
    """
    matrix comes here
    MATRIX={word:value,word2:value2}

    result: 
    [{word:value,word2:value2}]
    
    """
    vect = CountVectorizer(stop_words="english", token_pattern=r'(?u)\b[A-Za-z]+\b')
    bag_of_words = vect.fit_transform([doc])
    words = vect.get_feature_names()
    word_dict = vect.vocabulary_
    array = bag_of_words.toarray()

    doc_score = 0
    related_words = []
    for word in words:
        if word in settings.MATRIX:
            count = array[0][word_dict[word]]
            score = count * settings.MATRIX[word]
            doc_score += score
            related_words.append((word, score))
    return {
        'score': doc_score,
        'words': related_words
    }


def analyze_word(word):
    """
    matrix comes here
    MATRIX={word:value,word2:value2}

    result:
    None/Float value
    """
    return settings.MATRIX.get(word)


def _build_matrix(chunk=15):

    # daily_updown = DailyStock.objects.all().order_by("diff_yesterday")
    # daily_updown = daily_updown.values('year', 'month', 'date', 'diff_yesterday')
    #
    # minval = abs(min(map(itemgetter('diff_yesterday'), daily_updown)))
    # maxval = abs(max(map(itemgetter('diff_yesterday'), daily_updown)))
    # if minval > maxval:
    #     daily_updown = [dict(d, diff_yesterday=(
    #         d['diff_yesterday']) / minval) for d in daily_updown]
    # else:
    #     daily_updown = [dict(d, diff_yesterday=(
    #         d['diff_yesterday']) / maxval) for d in daily_updown]

    up_days = list(DailyStock.objects.order_by('diff_yesterday')[:chunk])
    down_days = list(DailyStock.objects.order_by('-diff_yesterday')[:chunk])

    max_diff = max(up_days[0].diff_yesterday, abs(down_days[0].diff_yesterday))
    daily_updown = up_days + down_days

    for daily in daily_updown:
        daily.diff_yesterday = daily.diff_yesterday / max_diff

    text_dict = {}
    days_text_list = []
    for daily in daily_updown:
        # dateconversion
        print(daily)
        LINK = 'https://news.google.com/rss/search?q=samsung+electronics+when:{}-{:02d}-{:02d}&hl=en-US&gl=US&ceid=US:en'.format(
            daily.year,
            daily.month,
            daily.date,
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
            singlelink = items.getElementsByTagName(
                'link')[0].firstChild.nodeValue
            pubdate = items.getElementsByTagName(
                'pubDate')[0].firstChild.nodeValue
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
        DailyDocument.objects.create(
            doc=today_text,
            is_up=daily.diff_yesterday > 0
        )

    scripts = days_text_list
    len(days_text_list)
    vectorizer = TfidfVectorizer(
        stop_words='english', token_pattern=r'(?u)\b[A-Za-z]+\b')
    bag_of_words = vectorizer.fit_transform(scripts)
    value_word = pd.DataFrame(bag_of_words.toarray()).mul(
        list(map(lambda d: d.diff_yesterday, daily_updown)), axis=0).sum(axis=0)
    string_word = vectorizer.get_feature_names()
    word_dict = {string_word[i]: value_word[i] for i in range(len(string_word))}
    with open('word_dict_pickle', 'wb') as f:
        pickle.dump(word_dict, f)
    return word_dict
