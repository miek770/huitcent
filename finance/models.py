from django.db import models
from django.contrib.auth.models import User
import time, re

class Group(models.Model):
    name = models.CharField(max_length=40)
    users = models.ManyToManyField(User)
    def __unicode__(self):
        return self.name

class Transaction(models.Model):
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return self.name + ' - ' + self.description

    def get_price_per_user(self):
        return self.price/Debtor.objects.filter(transaction__exact=self).count()

class Debtor(models.Model):
    user = models.ForeignKey(User)
    transaction = models.ForeignKey(Transaction)
    def __unicode__(self):
        return self.user.username + ' - ' + self.transaction.name
