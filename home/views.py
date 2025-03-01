from django.shortcuts import render, redirect
from django.views import View
from requests.models import Form
from datetime import datetime, timezone


class HomeView(View):
    def get(self, request):
        now = datetime.now(timezone.utc).astimezone()
        forms = Form.objects.filter(activated__lte=now, expired__gte=now)
        return render(request, 'home.html', {'forms': forms})
