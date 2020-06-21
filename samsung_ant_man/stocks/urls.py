from django.urls import path
from stocks.views import IndexView, AnalyzeDoc


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('analyze/', AnalyzeDoc.as_view(), name='analyze')
]
