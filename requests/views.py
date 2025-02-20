from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Form, Question, Answer, Submit
from accounts.forms import UsernameForm
from django.contrib.auth.models import User


class AnswerView(View):

    def get(self, request, form_slug):
        questions = Question.objects.prefetch_related('answers').all()
        forms = Form.objects.get(slug=form_slug)
        username = UsernameForm
        return render(request, 'question.html', {'questions': questions, 'forms': forms, 'username': username})

    def post(self, request, form_slug):
        username = request.POST.get('username')
        form = Form.objects.get(id=form_slug)
        user = User.objects.create(username=username)
        user_answers = {}
        for question in form.questions.all():
            user_answer_id = request.POST.get(str(question.id))
            user_answers[str(question.id)] = user_answer_id

        Submit.objects.create(
            user=user, form=form, answers=user_answers)
        return redirect('requests:result')  # نمایش صفحه‌ی نتایج


class ResultView(View):
    def get(self, request):
        return render(request, 'result.html')
