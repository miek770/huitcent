# -*- coding: utf-8 -*-

from forum.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
import math, os, re, subprocess, time
from datetime import datetime, timedelta
from operator import itemgetter
from django.middleware.csrf import get_token

from django.conf import settings

def get_todo_list(user):
    return ToDo.objects.filter(user__exact=user).order_by('done', '-priority', 'description')

def get_hidden_threads():
    delay = (datetime.now()-timedelta(365))
    return Thread.objects.filter(sticky__exact=False).filter(archived__exact=True).filter(date__lte=delay).count()

def check_right(request, forum_id):
    try:
        return Right.objects.filter(user__exact=request.user).get(forum__id__exact=forum_id).access
    except ObjectDoesNotExist:
        return False

def get_forum_list(request):
    base_forum_list = Forum.objects.only('name').order_by('name')
    right_list = Right.objects.only('user', 'forum', 'access').filter(user__exact=request.user.id)
    forum_list = []
    for forum in base_forum_list:
        access = False
        for right in right_list:
            if (forum == right.forum) and (right.access == True):
                access = True
        forum_list.append((forum, access))
    return forum_list

def get_pending_subscriptions():
    return Right.objects.filter(pending__exact=True).count()

def upload_file(file):
    timestamp = datetime.now().strftime("%y%m%d%f")
    filename = timestamp + "." + file.name.split(".")[-1]
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    with open(filepath, "wb+") as newfile:
        for chunk in file.chunks():
            newfile.write(chunk)
    return filename

def get_page(post, thread_id, pref):
    post_list = Post.objects.filter(thread__exact=thread_id)
    post_count = post_list.count()
    position = 0
    for p in post_list:
        if p == post: break
        position += 1
    page = int(math.ceil(float(position)/pref.posts_per_page))
    if page == 0: page = 1
    return page

def get_post_page_lists(request, thread_id, pref):
    try:
        page = float(request.GET.get('page', '0'))
    except ValueError:
        page = 0.0
    post_count = Post.objects.filter(thread__exact=thread_id).count()
    pages = math.ceil(float(post_count)/pref.posts_per_page)
    if pages == 0.0:
        pages = 1.0
    if (page == 0.0) or (page > pages):
        page = pages
    base_post_list = Post.objects.filter(thread__exact=thread_id).order_by('date')[(page-1)*pref.posts_per_page:page*pref.posts_per_page]
    post_list = []
    counter = 1
    for post in base_post_list:
        try:
            attachment = Attachment.objects.get(post__exact=post.id)
        except ObjectDoesNotExist:
            attachment = None
        try:
            avatar = Avatar.objects.get(user__exact=post.user)
        except ObjectDoesNotExist:
            avatar = None
        if NewPost.objects.filter(post__exact=post).filter(user__exact=request.user):
            new = True
        else:
            new = False
        if counter == len(base_post_list):
            post_list.append((post, attachment, avatar, new, True))
        else:
            post_list.append((post, attachment, avatar, new, False))
        counter += 1
        NewPost.objects.filter(post__exact=post).filter(user__exact=request.user).delete()
    page_list = range(1,1+int(pages))
    return post_list, page_list, page

def get_file(filename, raw=False):
    try:
        with open(filename) as file:
            output = file.read()
    except IOError:
        output = "Permission denied!"
    if raw:
        return output
    else:
        return output.replace('\n', '<br />')

def render(request, template, args={}, context=False):
    get_token(request)
    post_count = Post.objects.count()
    try:
        contribution = round(100.0*Post.objects.filter(user__exact=request.user).count()/post_count,1)
    except ZeroDivisionError:
        contribution = 0.0
#    dbox_total = get_file("/var/log/dbox.log").split('>')[1].split('\t')[0]
#    dbox_percent = str(int((float(dbox_total[:-1])/6.5)*100))
    dbox_total = '0'
    dbox_percent = '0'
    pref = Preference.objects.get(user__exact=request.user)
    arguments = {
        'user': request.user,
        'forum_list': get_forum_list(request),
        'pending': get_pending_subscriptions(),
        'hidden': get_hidden_threads(),
        'user_count': User.objects.count(),
        'forum_count': Forum.objects.count(),
        'topic_count': Topic.objects.count(),
        'thread_count': Thread.objects.count(),
        'post_count': post_count,
        'contribution': contribution,
        'dbox': (dbox_total, dbox_percent),
        'todo_list': get_todo_list(request.user),
        'pref': pref,
        }
    for key in args.keys():
        arguments[key] = args[key]
    return render_to_response(template, arguments, context_instance=RequestContext(request))

