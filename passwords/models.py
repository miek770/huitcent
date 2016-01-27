from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=50)
    details = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Password(models.Model):
    name = models.CharField(max_length=50)
    details = models.CharField(max_length=100)
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    group = models.ForeignKey(Group)
    def __str__(self):
        return self.name

class Account(models.Model):
  user = models.ForeignKey(User)
  group = models.ForeignKey(Group)

