# -*- coding: utf-8 -*-

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from forum.models import *
from forum.functions import get_todo_list

def _refresh_todo(user):
    dajax = Dajax()
    todo_list = get_todo_list(user)
    html = str()
    for t in todo_list:
        if t.priority == 5:
            html += '<tr class="todo_row" style="color: #CC0000">'
        elif t.priority == 4:
            html += '<tr class="todo_row" style="color: #993300">'
        elif t.priority == 3:
            html += '<tr class="todo_row" style="color: #666600">'
        elif t.priority == 2:
            html += '<tr class="todo_row" style="color: #339900">'
        elif t.priority == 1:
            html += '<tr class="todo_row" style="color: #00CC00">'
        html += ' <td class="todo_cell">'
        if t.done: html += '<del>'
        html += t.priority
        if t.done: html += '</del>'
        html += '</td>'
        html += ' <td class="todo_desc">'
        if t.done: html += '<del>'
        html += t.description
        if t.done: html += '</del>'
        html += '</td>'
        html += ' <td class="todo_cell">'
        html += '  <input'
        html += '   type="checkbox"'
        html += '   id="' + str(t.id) + '"'
        html += '   onchange="check_todo(this)"'
        if t.done: html += 'checked="checked" '
        html += '   />'
        html += ' </td>'
        html += '</tr>'
    dajax.assign('#todo_table_list', 'innerHTML', html)
    return dajax.json()

def _say_hello(msg="Hello world!"):
    dajax = Dajax()
    dajax.alert(msg)
    return dajax.json()

@dajaxice_register
def new_todo(request, form):
    todo = ToDo(user=request.user,
                priority=int(form['todo_priority']),
                description=form['todo_description'],
                done=False)
    todo.save()
    return _refresh_todo(request.user)

@dajaxice_register
def check_todo(request, id, value):
    todo = ToDo.objects.get(pk=id)
    todo.done = value
    todo.save()
    return _refresh_todo(request.user)

@dajaxice_register
def flush_todo(request):
    ToDo.objects.filter(user__exact=request.user).filter(done__exact=True).delete()
    return _refresh_todo(request.user)

@dajaxice_register
def set_visibility(request, item, show):
    pref = Preference.objects.get(user__exact=request.user)
    if item == 'show_todo':
        pref.show_todo = show
    elif item == 'show_admin':
        pref.show_admin = show
    pref.save()
    dajax = Dajax()
    return dajax.json()

@dajaxice_register
def clear_new_post(request, new_post):
    new_post = int(new_post)
    n = NewPost.objects.get(pk=new_post)
    user = n.user
    n.delete()

    new_posts_list = NewPost.objects.filter(user__exact=user)
    thread_list = []
    for np in new_posts_list:
        if not np.post.thread.id in thread_list:
            thread_list.append(np.post.thread.id)
    threads = len(thread_list)
    new_posts = new_posts_list.count()

    if new_posts > 1:
        if threads > 1:
            html = "Il y a "
            html += str(new_posts)
            html += " nouveaux messages dans "
            html += str(threads)
            html += " discussions :<br />"
        else:
            html = "Il y a "
            html += str(new_posts)
            html += " nouveaux messages dans 1 discussion :<br />"
    elif new_posts == 1:
            html = "Il y a 1 nouveau message dans 1 discussion :<br />"
    else:
            html = "Il n'y a pas de nouveau message.<br />"

    dajax = Dajax()
    dajax.clear('#new_post' + str(new_post), 'innerHTML')
    dajax.assign('#new_posts_summary', 'innerHTML', html)
    return dajax.json()
