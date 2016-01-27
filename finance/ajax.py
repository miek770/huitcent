from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.core.exceptions import ObjectDoesNotExist
from finance.models import *
from django.contrib.auth.models import User
from decimal import *

import datetime

@dajaxice_register
def get_debt(request, user1, user2, group):
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

    dajax = Dajax()
    dajax.assign(u'#debt' + unicode(user2),
                 u'innerHTML',
                 html)
    return dajax.json()

@dajaxice_register
def get_transaction(request, group_id, index):
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

    dajax = Dajax()
    dajax.append(u'#transactions', u'innerHTML', html)
    return dajax.json()

