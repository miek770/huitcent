# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from forum.models import *
from forum.functions import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import math

@login_required
def index(request):
    base_new_post_list = NewPost.objects.filter(user__exact=request.user)
    new_posts = len(base_new_post_list)
    thread_list = []
    for new_post in base_new_post_list:
        if not new_post.post.thread.id in thread_list:
            thread_list.append(new_post.post.thread.id)
    new_threads = len(thread_list)
    new_post_list = []
    for new_post in base_new_post_list:
        new_post_list.append((new_post.post, new_post.post.user, new_post.post.thread, new_post.post.thread.topic, new_post.post.thread.topic.category.forum, new_post))
    return render(request, template='forum/index.html', args={
        'new_post_list': new_post_list,
        'new_posts': new_posts,
        'new_threads': new_threads,
        })

@login_required()
def view_forum(request, forum_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)

    # La catégorie "Général" apparaît toujours en 1er
    category_list = list(Category.objects.filter(forum__exact=forum_id).order_by('name'))
    i=0
    for category in category_list:
        if category.name == u"Général":
            category_list.insert(0, category_list.pop(i))
            break
        i+=1

    # Le topic "Général" apparaît toujours en 1er
    base_topic_list = list(Topic.objects.filter(category__forum__exact=forum_id).order_by('name'))
    i=0
    for topic in base_topic_list:
        if topic.name == u"Général":
            base_topic_list.insert(0, base_topic_list.pop(i))
        i+=1

    right = Right.objects.filter(user__exact=request.user).get(forum__exact=forum)
    topic_list = []
    for topic in base_topic_list:
        try:
            last_thread = Thread.objects.filter(topic__exact=topic.id).latest('date')
            last_user = Post.objects.filter(thread__exact=last_thread.id).latest('date').user.username
        except ObjectDoesNotExist:
            last_thread = None
            last_user = None
        topic_list.append((topic, last_thread, last_user))
    return render(request, template='forum/view_forum.html', args={
        "forum": forum,
        "category_list": category_list,
        "topic_list": topic_list,
        "right": right,
        })

@login_required()
def new_forum(request):
    return render(request, template='forum/new_forum.html')

@login_required()
def create_forum(request):

    # Check if the forum name is empty
    if not request.POST['name']:
        message = "Erreur : Vous devez entrer un nom de forum."
        return render(request, template="forum/new_forum.html", args={
            "message": message,
            })


    # Check if this forum name is already taken
    forum_list = Forum.objects.all()
    for forum in forum_list:
        if request.POST['name'] == forum.name:
            message = "Error: That forum name is already used."
            return render(request, template='forum/new_forum.html', args={
                "message": message
                })

    # Otherwise, create it
    f = Forum(name=request.POST['name'])
    f.save()
    Right(forum=f, user=request.user, access=True, admin=True, pending=False).save()
    return view_forum(request, f.id)

@login_required()
def subscribe_to_forum(request, forum_id):
    forum = Forum.objects.get(pk=forum_id)
    return render(request, template='forum/subscribe.html', args={"forum": forum})

@login_required()
def do_subscribe_to_forum(request, forum_id):
    forum = Forum.objects.get(pk=forum_id)
    right_list = Right.objects.all()
    error = False
    for right in right_list:
        if (right.forum == forum) and (right.user == request.user):
            error = True
    if error:
        message = "Error: A subscription request for forum ' + forum.name + ' is already pending."
    else:
        Right(forum=forum, user=request.user).save()
        message = "A subscription request for forum ' + forum.name + ' was sent to the administrators."
    return render(request, template="forum/index.html", args={
        "message": message,
        })

@login_required()
def new_category(request, forum_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden!"
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    return render(request, template="forum/new_category.html", args={
        "forum": forum
        })

@login_required()
def create_category(request, forum_id):

    # Check if the user can access this forum
    if not check_right(request, forum_id):
        message = "Error: Forbidden!"
        return render(request, template="forum/index.html", args={
            "message": message,
            })

    forum = Forum.objects.get(pk=forum_id)

    # Check if the category name is empty
    if not request.POST['name']:
        message = "Erreur : Vous devez entrer une catégorie."
        return render(request, template="forum/new_category.html", args={
            "forum": forum,
            "message": message,
            })

    # Check if this category name is already taken
    category_list = Category.objects.filter(forum__exact=forum)
    for category in category_list:
        if request.POST['name'] == category.name:
            message = "Error: That category name is already used."
            return render(request, template="forum/new_category.html", args={
                "forum": forum,
                "message": message,
                })

    # Otherwise, create it
    c = Category(name=request.POST['name'], forum=forum)
    c.save()
    return view_forum(request, forum_id)

@login_required()
def view_topic(request, forum_id, topic_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    pref = Preference.objects.get(user__exact=request.user)
    try:
        page = float(request.GET.get('page', '1'))
    except ValueError:
        page = 1.0
    thread_count = Thread.objects.filter(topic__exact=topic_id).count()
    pages = math.ceil(float(thread_count)/pref.threads_per_page)
    if pages == 0.0:
        pages = 1.0
    if (page == 0.0) or (page > pages):
        page = pages

    thread_list = Thread.objects.filter(topic__exact=topic_id).order_by("-sticky", "-date")[(page-1)*pref.threads_per_page:page*pref.threads_per_page]

    page_list = range(1,1+int(pages))
    right = Right.objects.filter(user__exact=request.user).get(forum__exact=forum)
    return render(request, template="forum/view_topic.html", args={
        "forum": forum,
        "topic": topic,
        "thread_list": thread_list,
        "page": page,
        "page_list": page_list,
        "right": right,
        })

@login_required()
def new_topic(request, forum_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    category_list = Category.objects.filter(forum__exact=forum).order_by('name')
    topic_list = Topic.objects.filter(category__forum__exact=forum_id).order_by('name')
    if Category.objects.filter(forum__exact=forum).count() < 1:
        message = "Error: Please create a category first."
        return render(request, template="forum/view_forum.html", args={
            "forum": forum,
            "category_list": category_list,
            "topic_list": topic_list,
            "message": message,
            })
    return render(request, template="forum/new_topic.html", args={
        "forum": forum,
        "category_list": category_list
        })

@login_required()
def create_topic(request, forum_id):

    # Check if the user can access this forum
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })

    forum = Forum.objects.get(pk=forum_id)

    # Check if the topic name is empty
    if not request.POST['name']:
        message = "Erreur : Vous devez entrer une sujet."
        return render(request, template="forum/new_topic.html", args={
            "forum": forum,
            "message": message,
            })

    # Check if the topic name is already taken in this category
    category = Category.objects.get(pk=request.POST['category'])
    topic_list = Topic.objects.filter(category__exact=category)
    for topic in topic_list:
        if request.POST['name'] == topic.name:
            message = "Error: That topic name is already used."
            return render(request, template="forum/new_topic.html", args={
                "forum": forum,
                "message": message
                })

    # Otherwise, create it
    t = Topic(name=request.POST['name'], description=request.POST['description'], category=category)
    t.save()
    return view_forum(request, forum_id)

@login_required()
def do_delete_topic(request, forum_id, topic_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    if not Right.objects.filter(user__exact=request.user).get(forum__id__exact=forum_id).admin:
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    NewPost.objects.filter(post__thread__topic__exact=topic_id).delete()
    Attachment.objects.filter(post__thread__topic__exact=topic_id).delete()
    Post.objects.filter(thread__topic__exact=topic_id).delete()
    Topic.objects.get(pk=topic_id).delete()
    category_list = Category.objects.filter(forum__exact=forum_id).order_by('name')
    base_topic_list = Topic.objects.filter(category__forum__exact=forum_id).order_by('name')
    topic_list = []
    for topic in base_topic_list:
        try:
            last_thread = Thread.objects.filter(topic__exact=topic.id).latest('date')
            last_user = Post.objects.filter(thread__exact=last_thread.id).latest('date').user.username
        except ObjectDoesNotExist:
            last_thread = None
            last_user = None
        topic_list.append((topic, last_thread, last_user))
    return view_forum(request, forum_id)

@login_required()
def edit_topic(request, forum_id, topic_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    return render(request, template='forum/edit_topic.html', args={
        "forum": forum,
        "topic": topic,
        })

@login_required()
def do_edit_topic(request, forum_id, topic_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    if not Right.objects.filter(user__exact=request.user).get(forum__id__exact=forum_id).admin:
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    topic.name = request.POST["name"]
    topic.description = request.POST["description"]
    topic.save()
    return view_forum(request, forum_id)

@login_required()
def view_thread(request, forum_id, topic_id, thread_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    pref = Preference.objects.get(user__exact=request.user)
    post_list, page_list, page = get_post_page_lists(request, thread_id, pref)
    right = Right.objects.filter(user__exact=request.user).get(forum__exact=forum)
    return render(request, template="forum/view_thread.html", args={
        "forum": forum,
        "topic": topic,
        "thread": thread,
        "post_list": post_list,
        "page": page,
        "page_list": page_list,
        "right": right,
        })

@login_required()
def new_thread(request, forum_id, topic_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    return render(request, template='forum/new_thread.html', args={
        'forum': forum,
        'topic': topic,
        })

@login_required()
def create_thread(request, forum_id, topic_id):

    # Check if the user has access to this forum
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })

    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)

    # Check if the thread name is empty
    if not request.POST['name']:
        message = "Erreur : Vous devez entrer un titre."
        return render(request, template="forum/new_thread.html", args={
            'forum': forum,
            'topic': topic,
            "message": message,
            })

    # Check if the thread name is already taken
    thread_list = Thread.objects.filter(topic__exact=topic)
    for thread in thread_list:
        if request.POST['name'] == thread.name:
            message = "Error: That thread name is already used."
            return render(request, template='forum/new_thread.html', args={
                'forum': forum,
                'topic': topic,
                'message': message,
                })

    # Otherwise, create it
    t = Thread(name=request.POST['name'], description=request.POST['description'], topic=topic, date=timezone.now())
    t.save()
    p = Post(date=timezone.now(), message=request.POST['message'].replace('\n', '<br />'), user=request.user, thread=t)
    p.save()
    if request.FILES:
        Attachment(name=upload_file(request.FILES["file"]), post=p).save()
    right_list = Right.objects.filter(forum__exact=forum).exclude(user=request.user).filter(access__exact=True)
    for right in right_list:
        NewPost(user=right.user, post=p).save()
    return view_thread(request, forum_id, topic_id, t.id)

@login_required()
def do_delete_thread(request, forum_id, topic_id, thread_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    if not Right.objects.filter(user__exact=request.user).get(forum__id__exact=forum_id).admin:
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    NewPost.objects.filter(post__thread__exact=thread_id).delete()
    Attachment.objects.filter(post__thread__exact=thread_id).delete()
    Post.objects.filter(thread__exact=thread_id).delete()
    Thread.objects.get(pk=thread_id).delete()
    pref = Preference.objects.get(user__exact=request.user)
    try:
        page = float(request.GET.get('page', '1'))
    except ValueError:
        page = 1.0
    thread_count = Thread.objects.filter(topic__exact=topic_id).count()
    pages = math.ceil(float(thread_count)/pref.threads_per_page)
    if pages == 0.0:
        pages = 1.0
    if (page == 0.0) or (page > pages):
        page = pages
    thread_list = Thread.objects.filter(topic__exact=topic_id).order_by('-date')[(page-1)*pref.threads_per_page:page*pref.threads_per_page]
    page_list = range(1,1+int(pages))
    return view_topic(request, forum_id, topic_id)

@login_required()
def edit_thread(request, forum_id, topic_id, thread_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    return render(request, template='forum/edit_thread.html', args={
        'forum': forum,
        'topic': topic,
        'thread': thread,
        })

@login_required()
def do_edit_thread(request, forum_id, topic_id, thread_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    if not Right.objects.filter(user__exact=request.user).get(forum__id__exact=forum_id).admin:
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    thread.name = request.POST["name"]
    thread.description = request.POST["description"]
    try:
        if request.POST["sticky"]:
            thread.sticky = True
    except:
        thread.sticky = False
    try:
        if request.POST["archive"]:
            thread.archived = True
    except:
        thread.archived = False
    thread.save()
    return view_topic(request, forum_id, topic_id)

@login_required()
def new_post(request, forum_id, topic_id, thread_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    return render(request, template='forum/new_post.html', args={'forum': forum, 'topic': topic, 'thread': thread})

@login_required()
def create_post(request, forum_id, topic_id, thread_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    p = Post(date=timezone.now(), message=request.POST['message'].replace('\n', '<br />'), user=request.user, thread=thread)
    p.save()
    if request.FILES:
        Attachment(name=upload_file(request.FILES["file"]), post=p).save()
    thread.date = p.date
    thread.save()
    right_list = Right.objects.filter(forum__exact=forum).exclude(user=request.user).filter(access__exact=True)
    for right in right_list:
        NewPost(user=right.user, post=p).save()
    return view_thread(request, forum_id, topic_id, thread_id)

@login_required()
def do_delete_post(request, forum_id, topic_id, thread_id, post_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    right = Right.objects.filter(user__exact=request.user).get(forum__exact=forum)
    if (Post.objects.get(pk=post_id).user != request.user) and not right.admin:
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    NewPost.objects.filter(post__exact=post_id).delete()
    Attachment.objects.filter(post__exact=post_id).delete()
    Post.objects.get(pk=post_id).delete()
    pref = Preference.objects.get(user__exact=request.user)
    post_list, page_list, page = get_post_page_lists(request, thread_id, pref)
    return view_thread(request, forum_id, topic_id, thread_id)

@login_required()
def edit_post(request, forum_id, topic_id, thread_id, post_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    post = Post.objects.get(pk=post_id)
    existing_post = post.message.replace('<br />', '')
    return render(request, template='forum/edit_post.html', args={
        'forum': forum,
        'topic': topic,
        'thread': thread,
        'post': post,
        'existing_post': existing_post,
        })

@login_required()
def reply_post(request, forum_id, topic_id, thread_id, post_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    topic = Topic.objects.get(pk=topic_id)
    thread = Thread.objects.get(pk=thread_id)
    post = Post.objects.get(pk=post_id)
    quoted_post = '<div class="quote"><i>' + post.user.username + ' posted on ' + post.date.ctime() + ':</i><br />' + post.message.replace('<br />', '') + '</div>\n'
    return render(request, template='forum/reply_post.html', args={
        'forum': forum,
        'topic': topic,
        'thread': thread,
        'post': post,
        'quoted_post': quoted_post,
        })

@login_required()
def do_edit_post(request, forum_id, topic_id, thread_id, post_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    right = Right.objects.filter(user__exact=request.user).get(forum__exact=forum_id)
    if (Post.objects.get(pk=post_id).user != request.user) and not right.admin:
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    post = Post.objects.get(pk=post_id)
    post.message = request.POST['message'].replace('\n', '<br />')
    post.save()
    return view_thread(request, forum_id, topic_id, thread_id)

@login_required()
def search(request, forum_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    return render(request, template="forum/search.html", args={
        "forum": forum,
        })

@login_required()
def do_search(request, forum_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    forum = Forum.objects.get(pk=forum_id)
    tags = request.POST["search"].split()
    if len(tags) == 0:
        message = "Error: Please provide search parameters."
        return render(request, template="forum/search.html", args={
            "forum": forum,
            "message": message,
            })
    # Recherche de posts
    base_post_list = Post.objects.filter(thread__topic__category__forum__id__exact=forum_id).order_by("-date")
    for tag in tags:
        base_post_list = base_post_list.filter(message__icontains=tag)
    post_list = []
    for post in base_post_list:
        thread = Thread.objects.get(pk=post.thread.id)
        topic = Topic.objects.get(pk=thread.topic.id)
        pref = Preference.objects.get(user__exact=request.user)
        page = get_page(post, thread.id, pref)
        post_list.append((post, thread, topic, page))
    posts = base_post_list.count()
    # Recherche de threads
    base_thread_list = Thread.objects.filter(topic__category__forum__id__exact=forum_id).order_by("-date")
    for tag in tags:
        base_thread_list = base_thread_list.filter(name__icontains=tag)
    thread_list = []
    for thread in base_thread_list:
        topic = Topic.objects.get(pk=thread.topic.id)
        thread_list.append((thread, topic))
    threads = base_thread_list.count()
    return render(request, template="forum/search_results.html", args={
        "forum": forum,
        "post_list": post_list,
        "posts": posts,
        "thread_list": thread_list,
        "threads": threads,
        })

@login_required()
def unread(request, forum_id, topic_id, thread_id, post_id):
    if not check_right(request, forum_id):
        message = "Error: Forbidden."
        return render(request, template="forum/index.html", args={
            "message": message,
            })
    NewPost(user=request.user, post=Post.objects.get(pk=post_id)).save()
    return index(request)

@login_required()
def clear_new_post(request, new_post_id):
    NewPost.objects.get(pk=new_post_id).delete()
    return index(request)

@login_required()
def edit_preferences(request):
    preferences = Preference.objects.get(user__exact=request.user)
    return render(request, template='forum/edit_preferences.html', args={
        'preferences': preferences,
        })

@login_required()
def do_edit_preferences(request):
    p = Preference.objects.get(user__exact=request.user)
    p.posts_per_page = request.POST['posts_per_page']
    p.threads_per_page = request.POST['threads_per_page']
    p.save()
    try:
        a = Avatar.objects.get(user__exact=request.user)
    except ObjectDoesNotExist:
        a = Avatar(user=request.user)
    try:
        a.name=upload_file(request.FILES['avatar'])
        a.save()
    except:
        None
    return index(request)

