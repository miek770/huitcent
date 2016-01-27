from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
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

def get_debt(user1, user2, group):
    user1, user2, group = int(user1), int(user2), int(group)
    debt = Decimal(0)
    transactions = Transaction.objects.filter(group__id__exact=group)
    for transaction in transactions:
        debtors = Debtor.objects.filter(transaction__exact=transaction)
        if transaction.user.id == user1:
            user2_debtor = False
            for debtor in debtors:
                if debtor.user.id == user2:
                    debt -= Decimal(transaction.price)/Decimal(len(debtors))
                    break
        elif transaction.user.id == user2:
            user1_debtor = False
            for debtor in debtors:
                if debtor.user.id == user1:
                    user1_debtor = True
                    debt += Decimal(transaction.price)/Decimal(len(debtors))
                    break
    total = debt.quantize(Decimal('.01'))
    if total>0:
        html = u'<div class="red">' + unicode(total) + u'$</div><br />'
    else:
        html = u'<div class="green">' + unicode(total) + u'$</div><br />'

    # To be revised (tuple of dajax items previously returned)
    # Obviously we won't be returning html anymore
    return ('#debt{}'.format(user2), 'innerHTML', html)

def get_transaction(group_id, index):
    members = User.objects.filter(group__exact=group_id).order_by('username')
    debts = []
    for member in members:
        if not member == request.user:
            debts.append((member, ))

    debtors_span = len(members)
    columns = debtors_span + 6
    base_transaction = Transaction.objects.filter(group__exact=group_id).order_by('-date')[int(index)]
    if request.user == base_transaction.user:
        transaction = (base_transaction, [], True)
    else:
        transaction = (base_transaction, [], False)
    transaction[0].price = Decimal(transaction[0].price).quantize(Decimal('.01'))
    debtors_qty = Debtor.objects.filter(transaction__exact=transaction[0]).count()
    if debtors_qty > 0:
        for member in members:
            try:
                Debtor.objects.filter(user__exact=member).get(transaction__exact=transaction[0])
                transaction[1].append((Decimal(transaction[0].price) / Decimal(debtors_qty)).quantize(Decimal('.01')))
            except ObjectDoesNotExist:
                transaction[1].append(Decimal(0).quantize(Decimal('.01')))

    html = u'<tr>\n'
    html += u' <td class="transactions" align="left">' + unicode(transaction[0].user.username) + u'</td>\n'
    html += u' <td class="transactions" align="left">' + unicode(transaction[0].name) + u'</td>\n'
    html += u' <td class="transactions" align="left">' + unicode(transaction[0].description) + u'</td>\n'
    html += u' <td class="transactions" align="center">' + unicode(transaction[0].date.ctime()) + u'</td>\n'
    html += u' <td class="transactions" align="right">' + unicode(transaction[0].price) + u'$</td>\n'
    for debt in transaction[1]:
        html += u' <td class="transactions" align="right">' + unicode(debt) + u'$</td>\n'
    html += u' <td class="transactions" align="center">\n'
    if transaction[2]:
        html += u'  <input type="button" onclick="confirm_del(' + unicode(transaction[0].id) + ')" value="Effacer" />\n'
    html += u' </td>\n'
    html += u'</tr>\n'

    # To be revised (tuple of dajax items previously returned)
    # Obviously we won't be returning html anymore
    return ('#transactions', 'innerHTML', html)

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

    # Create members / debtors list
    members = User.objects.filter(group__exact=group).order_by('username')
    debts = []
    for member in members:
        if not member == request.user:
            debts.append((member, ))
    debtors_span = len(members)
    columns = debtors_span + 6

    # Create list of ALL transactions in this group
    transactions = range(len(Transaction.objects.filter(group__exact=group).order_by('-date')))

    return render(request, template='finance/view_group.html', args={
                  'group': group,
                  'members': members,
                  'debtors_span': debtors_span,
                  'columns': columns,
                  'transactions': transactions,
                  'debts': debts,
                  }, context=True)

@login_required()
def new_group(request):
    return render(request, template='finance/new_group.html', context=True)

@login_required()
def create_group(request):

    # Check if the group name is already taken
    groups = Group.objects.all()
    for g in groups:
        if request.POST['Name'] == g.name:
            message = "Erreur : Ce nom de groupe est déjà utilisé."
            return render(request, template="finance/new_group.html", args={
                'message': message,
                }, context=True)

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
        }, context=True)

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
