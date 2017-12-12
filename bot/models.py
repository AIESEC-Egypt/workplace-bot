from __future__ import unicode_literals

from datetime import datetime
from django.db import models

# Create your models here.

class Member(models.Model):
    name = models.CharField(max_length=128)
    STATUS_CHOICES = (
        ("1", "Busy"),
        ("2", "Available")
    )
    current_survey_id = models.IntegerField(null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)


class Question(models.Model):
    text = models.CharField(max_length=512)
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
    start_time = models.TimeField(default=datetime.now())
    end_time = models.TimeField(default=datetime.now())
    title = models.CharField(max_length=128)
    
