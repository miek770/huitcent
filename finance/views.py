# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from finance.models import *
from forum.functions import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import *

def is_member(user, group):
    try:
        User.objects.filter(username__exact=user.username).get(group__exact=group)
        return True
    except ObjectDoesNotExist:
        return False

@login_required()
def index(request):
    base_groups = Group.objects.all().order_by('name')
    groups = []
    for group in base_groups:
        members = User.objects.filter(group__exact=group).order_by('username')
        debts = []
        membership = is_member(request.user, group)
        if membership:
            for member in members:
                if not member == request.user:
                    debts.append((member,))
        groups.append((group, debts, membership))
    return render(request, template='finance/index.html', args={
        'groups': groups,
        })

@login_required()
def view_group(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)

    # This group doesn't exist
    except ObjectDoesNotExist:
        return render(request,
                      template='forum/output.html',
                      args={'output': 'ERROR: Finance - Group does not exist.'})

    # Check if the user is a member of the group
    if not is_member(request.user, group):
        return render(request,
                      template='forum/output.html',
                      args={'output': 'ERROR: Finance - You are not part of this group.'})

    # Génère la liste des membres du groupe, autres que l'utilisateurs principal
    members = User.objects.filter(group__exact=group).order_by('username')
    debts = list()
    for member in members:
        if not member == request.user:
            debts.append([member, None])
    debtors_span = len(members)
    columns = debtors_span + 6

    # Génère la liste des transactions du groupe
    base_transaction_list = Transaction.objects.filter(group__exact=group_id).filter(fused__exact=False).order_by('-date')
    transactions = list()

    for base_transaction in base_transaction_list:

        # transaction = [objet Transaction,
        #                liste de débits (en $),
        #                l'utilisateur est-il le créditeur?,
        #                coût par débiteur,
        #                liste de sous-transactions (fusionnées)]

        # L'utilisateur est le créditeur de cette transaction
        if request.user == base_transaction.user:
            transaction = [base_transaction, list(), True, None, list()]

        # L'utilisateur est un débiteur de cette transaction
        else:
            transaction = [base_transaction, list(), False, None, list()]

        debtors_qty = Debtor.objects.filter(transaction__exact=transaction[0]).count()

        if debtors_qty > 0:

            # Calcule le coût par débiteur pour cette transaction
            transaction[3] = (Decimal(transaction[0].price) / Decimal(debtors_qty)).quantize(Decimal('.01'))

            for member in members:

                # Le membre est débiteur de cette transaction
                try:
                    Debtor.objects.filter(user__exact=member).get(transaction__exact=transaction[0])
                    transaction[1].append(transaction[3])

                # Le membre n'est pas impliqué sur cette transaction
                except ObjectDoesNotExist:
                    transaction[1].append(Decimal(0).quantize(Decimal('.01')))

        # Si la transaction est une fusion, lui annexer les transactions fusionnées
        if transaction[0].fusion:
            transaction[4] = Transaction.objects.filter(fused_into__exact=transaction[0]).order_by("-date")

        transactions.append(transaction)

    # Calcule les dettes combinées
    for debt in debts:
        d = Decimal(0)
        for transaction in transactions:

            # Monte une liste des débiteurs pour cette transaction
            debtors = Debtor.objects.filter(transaction__exact=transaction[0])

            # L'utilisateur est le créditeur de cette transaction
            if transaction[2]:
                for debtor in debtors:
                    if debtor.user == debt[0]:
                        d -= transaction[3]
                        break

            # Le 2e utilisateur est le créditeur de cette transaction
            elif transaction[0].user == debt[0]:
                for debtor in debtors:
                    if debtor.user == request.user:
                        d += transaction[3]
                        break

        debts[debts.index(debt)][1] = d

    return render(request, template='finance/view_group.html', args={
                  'group': group,
                  'members': members,
                  'debtors_span': debtors_span,
                  'columns': columns,
                  'transactions': transactions,
                  'debts': debts,
                  })

@login_required()
def new_group(request):
    return render(request, template='finance/new_group.html')

@login_required()
def create_group(request):

    # Check if the group name is already taken
    groups = Group.objects.all()
    for g in groups:
        if request.POST['Name'] == g.name:
            message = "Erreur : Ce nom de groupe est déjà utilisé."
            return render(request, template="finance/new_group.html", args={
                'message': message,
                })

    # Otherwise, create it
    group = Group(name=request.POST['Name'])
    group.save()
    group.users.add(request.user)
    return index(request)

@login_required()
def add_member(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
    except ObjectDoesNotExist:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Group does not exist.'})
    if not is_member(request.user, group):
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - You are not part of this group.'})
    users = User.objects.exclude(group__exact=group).order_by('username')
    return render(request, template='finance/add_member.html', args={
        'group': group,
        'users': users,
        })

@login_required()
def do_add_member(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
    except ObjectDoesNotExist:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Group does not exist.'})
    if not is_member(request.user, group):
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - You are not part of this group.'})
    user = User.objects.get(username__exact=request.POST['name'])
    group.users.add(user)
    return view_group(request, group_id)

@login_required()
def add_transaction(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
    except ObjectDoesNotExist:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Group does not exist.'})
    if not is_member(request.user, group):
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - You are not part of this group.'})
    if request.POST['price'] == '':
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Invalid data.'})
    try:
        transaction = Transaction(
            group=group,
            name=request.POST['name'],
            description=request.POST['description'],
            date=timezone.now(),
            price=Decimal(request.POST['price'].replace(',', '.')).quantize(Decimal('.01')),
            user=request.user,
            fused=False,
            )
    except:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Invalid data.'})
    transaction.save()
    for field in request.POST:
        if 'chk_' in field:
            try:
                user = User.objects.get(username__exact=field.split('chk_')[1])
                debtor = Debtor(user=user, transaction=transaction)
                debtor.save()
            except ObjectDoesNotExist:
                return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - User does not exist.'})
    return view_group(request, group_id)

@login_required()
def delete_transaction(request, group_id, transaction_id):
    try:
        group = Group.objects.get(pk=group_id)
    except ObjectDoesNotExist:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Group does not exist.'})
    try:
        transaction = Transaction.objects.get(pk=transaction_id)
    except ObjectDoesNotExist:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - Transaction does not exist.'})
    if not is_member(request.user, group):
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - You are not part of this group.'})
    if not request.user == transaction.user:
        return render(request, template='forum/output.html', args={'output': 'ERROR: Finance - You are not the debitor of this transaction.'})
    transaction.delete()
    return view_group(request, group_id)
