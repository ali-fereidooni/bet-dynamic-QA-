from django.db import models


class Answer(models.Model):
    answer = models.CharField(max_length=500)
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
    username = models.BooleanField(default=False)
    phone_number = models.BooleanField(default=False)
    activated = models.DateTimeField(null=True, blank=True)
    expired = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Users(models.Model):
    username = models.CharField(
        max_length=20, unique=True, null=True, blank=True)
    phone_number = models.CharField(
        max_length=11, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username


class Submit(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    answers = models.JSONField()  # Store answers as a JSON field

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.form.name} - {self.answers}"


class ImageModel(models.Model):
    title = models.CharField(max_length=15)
    image = models.ImageField(upload_to='images/')
