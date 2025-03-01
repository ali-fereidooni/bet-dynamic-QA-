from django.shortcuts import render, redirect
from django.views import View
from django.db import IntegrityError
from django.contrib import messages
from .models import Form, Question, Submit, Users, Answer, ImageModel
from .forms import DynamicUserForm, FormModelForm
from datetime import datetime, timezone


class AnswerView(View):

    def get(self, request, form_slug):
        form_instance = Form.objects.get(slug=form_slug)
        activate = form_instance.activated
        expired = form_instance.expired
        now = datetime.now(timezone.utc).astimezone()
        if activate > now or now > expired:
            return redirect('home:home')
        questions = form_instance.questions.prefetch_related('answers').all()
        user_form = DynamicUserForm(form_instance=form_instance)
        images = ImageModel.objects.all()

        return render(request, 'question.html', {
            'questions': questions,
            'form': form_instance,
            'user_form': user_form,
            'images': images
        })

    def post(self, request, form_slug):
        form_instance = Form.objects.get(slug=form_slug)
        user_form = DynamicUserForm(request.POST, form_instance=form_instance)

        if user_form.is_valid():
            user_data = user_form.cleaned_data
            username = user_data.get('username')
            phone_number = user_data.get('phone_number')

            # Check if the user has already submitted this form
            if Submit.objects.filter(user__username=username, form=form_instance).exists():
                messages.error(
                    request, "You have already submitted this form.")
                return render(request, 'question.html', {
                    'questions': form_instance.questions.all(),
                    'form': form_instance,
                    'user_form': user_form
                })

            try:
                new_user, created = Users.objects.get_or_create(
                    username=username,
                    defaults={'phone_number': phone_number}
                )

                # Save user's answers
                user_answers = {}
                for question in form_instance.questions.all():
                    user_answer_id = request.POST.get(str(question.id))
                    answer = Answer.objects.get(id=user_answer_id)
                    user_answers[question.title] = answer.answer

                submit = Submit.objects.create(
                    user=new_user, form=form_instance, answers=user_answers
                )

                # Create a dictionary of questions and their corresponding answers
                question_answers = {}
                for question in form_instance.questions.all():
                    answer_title = user_answers.get(str(question.title))
                    answer = Answer.objects.get(answer=answer_title)
                    question_answers[question] = answer

                return render(request, 'result.html', {
                    'submit': submit,
                    'questions': form_instance.questions.all(),
                    'question_answers': question_answers
                })

            except IntegrityError:
                messages.error(
                    request, "This username is already taken. Please choose a different username.")

        return render(request, 'question.html', {
            'questions': form_instance.questions.all(),
            'form': form_instance,
            'user_form': user_form
        })


class ResultView(View):
    def get(self, request):
        return render(request, 'result.html')
