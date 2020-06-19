from django.views.generic import TemplateView
from stocks.models import DailyStock


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        daily_stocks = DailyStock.objects.filter(date=1).all()
        context['latest_stock'] = DailyStock.objects.last()
        context['stock_prices'] = list(map(lambda x: x.current_price, daily_stocks))
        context['stock_labels'] = list(map(lambda x: str(x), daily_stocks))
        return context
