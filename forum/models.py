# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.forms import ModelForm, CharField
from django.utils import timezone
import time, re

class Forum(models.Model):
    name = models.CharField(max_length=40)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=40)
    forum = models.ForeignKey(Forum)
    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100)
    category = models.ForeignKey(Category)
    archive = models.BooleanField(default=False)

    def get_last_thread(self):
        try:
            return Thread.objects.filter(topic__exact=self.id).latest('date')
        except IndexError:
            return None

    def get_last_user(self):
        try:
            p = Post.objects.filter(thread__topic__exact=self.id).only('date', 'user').latest('date')
            return p.user.username
        except IndexError:
            return None

    def get_posts(self):
        return Post.objects.filter(thread__topic__exact=self.id).count()

    def get_threads(self):
        return Thread.objects.filter(topic__exact=self.id).count()

    def __str__(self):
        return self.name

class Thread(models.Model):
    name = models.CharField(max_length=40)
    date = models.DateTimeField()
    description = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic)
    archived = models.BooleanField(default=False)
    sticky = models.BooleanField(default=False)

    def get_posts(self):
        return Post.objects.filter(thread__exact=self.id).count()

    def get_last_post(self):
        try:
            return Post.objects.filter(thread__exact=self.id).latest('date')
        except IndexError:
            return None

    def hidden(self):
        if self.archived and not self.sticky:
            if self.date < (timezone.now()-timezone.timedelta(365)):
                return True
        return False

    def __str__(self):
        return self.name

class Post(models.Model):
    message = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    thread = models.ForeignKey(Thread)

    def get_user_posts(self):
        return Post.objects.filter(user__exact=self.user).count()

    def get_summary(self):
        if len(self.message) > 400:
            data = self.message[:400] + '...'
        else:
            data = self.message
        tmp = re.compile(r'<.*?>')
        return tmp.sub('', data)

    def __str__(self):
        return self.date.ctime()

class NewPost(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    def __str__(self):
        return self.user.username + ' ' + self.post.message[:30]

class Attachment(models.Model):
    name = models.CharField(max_length=100)
    post = models.ForeignKey(Post)
    def __str__(self):
        return self.name

class Avatar(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username

class Preference(models.Model):
    user = models.OneToOneField(User)
    posts_per_page = models.IntegerField(default=10)
    threads_per_page = models.IntegerField(default=10)
    show_todo = models.BooleanField(default=False)
    show_admin = models.BooleanField(default=True)
    def __str__(self):
        return self.user.username

class Right(models.Model):
    user = models.ForeignKey(User)
    forum = models.ForeignKey(Forum)
    access = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    def __str__(self):
        if self.pending:
            return self.user.username + ' ' + self.forum.name + ' (pending)'
        else:
            return self.user.username + ' ' + self.forum.name

class TopicAdmin(admin.ModelAdmin):
    list_display = ("__str__", "description", "category")
    list_filter = ("archive",)
    ordering = ["__str__"]

class ThreadAdmin(admin.ModelAdmin):
    list_display = ("__str__", "description", "topic", "date", "sticky", "hidden")
    list_filter = ("archived",)
    ordering = ["-date"]

class RightAdmin(admin.ModelAdmin):
    list_display = ("user", "forum", "access", "admin", "pending")
    list_filter = ("pending", "user", "forum")
    ordering = ["user"]

