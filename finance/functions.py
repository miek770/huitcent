# -*- coding: utf-8 -*-

from finance.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime, timedelta
from itertools import product
from decimal import *

def ct(age=timedelta(28)):

    groups = Group.objects.all()

    for group in groups:

        users = User.objects.filter(group__exact=group).order_by("username")

        for user in users:
            print(user.username)

        for creditor in users:

            for user in users:

                transactions = Transaction.objects.filter(group__exact=group).filter(user__exact=creditor)

                truth_table = list(product([False, True], repeat=len(users)))

                for case in truth_table:
                    print("Débiteurs : {}".format(case))
                    total = Decimal(0)
                    fusion = 0

                    for transaction in transactions:

                        match = True
                        i=0
                        for debtor in case:
                            try:
                                Debtor.objects.filter(transaction__exact=transaction).get(user__exact=users[i])
                                if not case[i]:
                                    match = False
                                    break

                            except ObjectDoesNotExist:
                                if case[i]:
                                    match = False
                                    break

                            i += 1

                        if match:
                            print("Transaction retenue : {}".format(transaction.description))
                            total += transaction.price
                            fusion += 1

                    print("{} transactions fusionnées, total = {}$".format(fusion, total))

                    t = Transaction(group=group,
                            name="Fusion",
                            description="Transactions de plus de X jours",
                            date=datetime.now(),
                            price=total,
                            user=request.user,
                            fused=False,
                            )

                break

            break

        break

