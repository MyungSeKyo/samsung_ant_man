import pickle
import urllib.request

import pandas as pd
from dateutil import parser as date_parser
from django.conf import settings
from goose3 import Goose
from requests import get
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from xml.dom import minidom
import re
from nltk.tag import pos_tag, untag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


# from stocks.models import WordProsCons, DailyStock
from stocks.models import DailyStock, DailyDocument


def analyze_doc(doc):
    """
    matrix comes here
    MATRIX={word:value,word2:value2}

    result: 
    [{word:value,word2:value2}]
    
    """
    if not doc:
        return {
            'score': 0,
            'words': [],
            'is_valid': False
        }
    vect = CountVectorizer(stop_words="english", token_pattern=r'(?u)\b[A-Za-z]+\b')
    bag_of_words = vect.fit_transform([doc])
    words = vect.get_feature_names()
    word_dict = vect.vocabulary_
    array = bag_of_words.toarray()

    doc_score = 0
    related_words = []
    is_valid = False
    for word in words:
        if word in settings.MATRIX:
            is_valid = True
            count = array[0][word_dict[word]]
            score = count * settings.MATRIX[word]
            doc_score += score
            related_words.append((word, score))

    return {
        'score': doc_score,
        'words': related_words,
        'is_valid': is_valid
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
    documents = []
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
    lemmatizer = WordNetLemmatizer()

    for sen in range(0, len(scripts)):
        # Remove all the special characters
        document = re.sub(r'\W', ' ', str(scripts[sen]))

        # remove all single characters
        document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)

        # Remove single characters from the start
        document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)

        # Substituting multiple spaces with single space
        document = re.sub(r'\s+', ' ', document, flags=re.I)

        # Converting to Lowercase
        document = document.lower()

        # Lemmatization
        document = document.split()
        doc = pos_tag(document)
        final_doc = []

        for i in range(len(doc)):
            if doc[i][1] in ['NN', 'NNP', 'NNS', 'NNPS']:
                document[i] = lemmatizer.lemmatize(document[i], 'n')
                final_doc.append(document[i])

            elif doc[i][1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                document[i] = lemmatizer.lemmatize(document[i], 'v')
                final_doc.append(document[i])

            elif doc[i][1] in ['JJ', 'JJR', 'JJS']:
                document[i] = lemmatizer.lemmatize(document[i], 'a')
                final_doc.append(document[i])

            elif doc[i][1] in ['RB', 'RBR', 'RBS', 'RP']:
                document[i] = lemmatizer.lemmatize(document[i], 'r')
                final_doc.append(document[i])


            #else:
            #    final_doc.append(document[i])

        pre_document = ' '.join(final_doc)
        documents.append(pre_document)

    vectorizer = TfidfVectorizer(
        stop_words='english', token_pattern=r'(?u)\b[A-Za-z]+\b', max_df=0.7)
    bag_of_words = vectorizer.fit_transform(documents)
    value_word = pd.DataFrame(bag_of_words.toarray()).mul(
        list(map(lambda d: d.diff_yesterday, daily_updown)), axis=0).sum(axis=0)
    string_word = vectorizer.get_feature_names()
    word_dict = {string_word[i]: value_word[i] for i in range(len(string_word))}
    with open('word_dict_pickle', 'wb') as f:
        pickle.dump(word_dict, f)
    return word_dict
