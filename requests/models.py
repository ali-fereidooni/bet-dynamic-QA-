from django.db import models
from django.contrib.auth.models import User


class Answer(models.Model):
    answer = models.CharField(max_length=500)
    # اضافه کردن فیلد برای مشخص کردن پاسخ صحیح
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer


class Question(models.Model):
    title = models.CharField(max_length=255)
    answers = models.ManyToManyField(Answer)

    def __str__(self):
        return self.title


class Form(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField(Question)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Submit(models.Model):
    # اصلاح برای ذخیره‌ی کاربر
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    answers = models.JSONField()  # ذخیره‌ی پاسخ‌ها در یک فیلد JSON

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.form.name}"
