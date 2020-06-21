import json

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
        analyze_doc(doc)
        return JsonResponse({})

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AnalyzeDoc, self).dispatch(request, *args, **kwargs)