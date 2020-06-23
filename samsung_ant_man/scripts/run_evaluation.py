from stocks.models import DailyDocument
from core.ir_analyzer import analyze_doc


def run():
    tp, fp, fn, tn = 0, 0, 0, 0
    for daily_doc in DailyDocument.objects.all():
        score = analyze_doc(daily_doc.doc).get('score')
        if str(daily_doc) == 'True':
            if score > 0:
                tp+=1
            else:
                fn+=1
        else:
            if score>0:
                fp+=1
            else:
                tn+=1

    P = tp / (tp+fp)
    R = tp / (tp+fn)
    print('Precision: {}'.format(P))
    print('Recall: {}'.format(R))
    F = (2*P*R) / (P+R)
    print('F-measure: {}'.format(F))
