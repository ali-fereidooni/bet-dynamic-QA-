from django.urls import path
from .views import AnswerView, ResultView

app_name = 'requests'
urlpatterns = [
    path('form/<slug:form_slug>/', AnswerView.as_view(), name='form'),
    path('result/', ResultView.as_view(), name='result'),
]
