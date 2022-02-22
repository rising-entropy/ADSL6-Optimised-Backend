from unicodedata import name
from django.db import models
from django.contrib.auth.models import User
from django.db.models import OneToOneField

class Quiz(models.Model):
    name = models.CharField(max_length=5000)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.CharField(max_length=5000)
    imageLink = models.CharField(max_length=5000, default="")
    option1 = models.CharField(max_length=1000)
    option2 = models.CharField(max_length=1000)
    option3 = models.CharField(max_length=1000)
    option4 = models.CharField(max_length=1000)
    correctAnswer = models.CharField(max_length=1000)

class Score(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, default=None)
    score = models.IntegerField()
    questionCount = models.IntegerField(default=0)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
