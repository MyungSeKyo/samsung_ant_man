from django.urls import path
from stocks.views import IndexView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]
