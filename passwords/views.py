# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import RequestContext
from passwords.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forum.models import Forum, Right
from forum.functions import *

@login_required()
def index(request):
    account_list = Account.objects.all().filter(user=request.user)
    group_list = []
    for account in account_list:
        group_list.append(Group.objects.get(id=account.group.id))
    forum_list = Forum.objects.all().order_by('name')
    return render(request, 'passwords/index.html', {'group_list': group_list})

@login_required()
def group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    password_list = Password.objects.all().filter(group=group).order_by('name')
    return render(request, 'passwords/group.html', {'group': group, 'password_list': password_list})

@login_required()
def new_group(request):
    return render(request, 'passwords/new_group.html')

@login_required()
def create_group(request):
    group = Group()
    group.name = request.POST['Name']
    group.details = request.POST['Details']
    group.save()
    account = Account(user=request.user, group=group).save()
    return index(request)

@login_required()
def edit_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    return render(request, 'passwords/edit_group.html', {'group': group})

@login_required()
def save_group(request, group_id):
    grp = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    grp.name = request.POST['Name']
    grp.details = request.POST['Details']
    grp.save()
    return group(request, group_id)

@login_required()
def do_delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    passwords = Password.objects.all().filter(group=group).count()
    if passwords == 0:
        group.delete()
        return index(request)
    else:
        group = get_object_or_404(Group, pk=group_id)
        password_list = Password.objects.all().filter(group=group).order_by('name')
        return render(request, 'passwords/group.html', {
            'group': group,
            'password_list': password_list,
            'message': "Error: Group " + group.name + " not empty!",
            })

@login_required()
def password(request, group_id, password_id):
    group = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    password = get_object_or_404(Password, pk=password_id)
    return render(request, 'passwords/password.html', {'group': group, 'password': password})

@login_required()
def new_password(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    return render(request, 'passwords/new_password.html', {'group': group})

@login_required()
def create_password(request, group_id):
    grp = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    pwd = Password()
    pwd.name = request.POST['Name']
    pwd.details = request.POST['Details']
    pwd.user = request.POST['User']
    pwd.password = request.POST['Password']
    pwd.group = grp
    pwd.save()
    return password(request, group_id, pwd.id)

@login_required()
def edit_password(request, group_id, password_id):
    group = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    password = get_object_or_404(Password, pk=password_id)
    forum_list = Forum.objects.all().order_by('name')
    return render(request, 'passwords/edit_password.html', {'group': group, 'password': password})

@login_required()
def save_password(request, group_id, password_id):
    grp = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    pwd = get_object_or_404(Password, pk=password_id)
    pwd.name = request.POST['Name']
    pwd.details = request.POST['Details']
    pwd.user = request.POST['User']
    pwd.password = request.POST['Password']
    pwd.save()
    return password(request, grp.id, pwd.id)

@login_required()
def do_delete_password(request, group_id, password_id):
    grp = get_object_or_404(Group, pk=group_id)

    # Vérifie que l'utilisateur a accès à ce groupe
    if request.user != get_object_or_404(Account, group=group_id).user:
        return redirect('/passwords')

    pwd = get_object_or_404(Password, pk=password_id)
    pwd.delete()
    return group(request, group_id)

