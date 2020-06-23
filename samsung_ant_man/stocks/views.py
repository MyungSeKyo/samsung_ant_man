import json
from math import ceil

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.ir_analyzer import analyze_doc

from stocks.models import DailyStock


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        daily_stocks = DailyStock.objects.filter(index_in_page=2).order_by('-id')
        context['latest_stock'] = DailyStock.objects.first()
        context['stock_prices'] = json.dumps(list(map(lambda x: x.current_price, daily_stocks)))
        context['stock_labels'] = json.dumps(list(map(lambda x: str(x), daily_stocks)))
        return context


class AnalyzeDoc(View):
    def post(self, request, *args, **kwargs):
        doc = request.POST.get('doc', 'china is attacking')
        result = analyze_doc(doc)

        if result['is_valid']:
            total = sum(map(lambda x: abs(x[1]), result['words']))
            max_val = max(map(lambda x: abs(x[1]), result['words']))
            max_size = 100
            ret = {
                'score': result['score'],
                'is_valid': result['is_valid'],
                'negative_words': [],
                'positive_words': [],
            }

            for word, val in result['words']:
                if val < 0:
                    ret['negative_words'].append({
                        'word': word,
                        'value': val / total,
                        'size': ceil((val / max_val) * max_size),
                    })
                else:
                    ret['positive_words'].append({
                        'word': word,
                        'value': val / total,
                        'size': ceil((val / max_val) * max_size),
                    })
            ret['positive_words'] = sorted(ret['positive_words'], key=lambda x: x['value'])
            ret['negative_words'] = sorted(ret['negative_words'], key=lambda x: x['value'])
            return JsonResponse(ret)
        else:
            return JsonResponse(result)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AnalyzeDoc, self).dispatch(request, *args, **kwargs)