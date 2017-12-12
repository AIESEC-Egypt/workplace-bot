from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


# Create your models here.

class Member(models.Model):
    name = models.CharField(max_length=128)
    STATUS_CHOICES = (
        ("1", "Busy"),
        ("2", "Available")
    )
    current_question = models.ForeignKey("Question", null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)


    def __str__(self):
        return self.name

    def next_question(self, message):
        answer = Answer(text=message, question=self.current_question)
        answer.save()

        current_question = self.current_question
        try:
            next_question = Question.objects.get(survey=current_question.survey.id, order=current_question.order + 1)
            self.current_question = next_question
            self.save()
            return self.current_question
        except ObjectDoesNotExist:
            self.status = "2"
            return None


class Question(models.Model):
    text = models.CharField(max_length=512)
    order = models.IntegerField()
    TYPE_CHOICES = (
        ("1", "Message"),
        ("2", "Postback")
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    survey = models.ForeignKey("Survey", on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Answer(models.Model):
    text = models.CharField(max_length=512)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    user = models.ForeignKey(Member, on_delete=models.CASCADE)


class Survey(models.Model):
    start_time = models.TimeField(auto_now=True)
    end_time = models.TimeField(auto_now=True)
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title
