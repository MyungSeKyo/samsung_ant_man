from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['daily_stock_values'] = [
            '10000',
            '20000',
            '30000',
            '40000',
            '20000',
        ]
        context['daily_stock_labels'] = [
            '20200101',
            '20200101',
            '20200101',
            '20200101',
            '20200101',
        ]
        return context
