# -*- coding: utf-8 -*-

from finance.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from datetime import timedelta
from django.utils import timezone
from itertools import product
from decimal import *

class Command(BaseCommand):
    help = "Combine les transactions similaires de plus de X jours (défini en argument)."

    def add_arguments(self, parser):
        parser.add_argument("jours", nargs=1, type=int)

    def handle(self, *args, **options):

        age=timedelta(options["jours"][0])

        groups = Group.objects.all()

        for group in groups:

            # On débute par effacer toutes les fusions précédentes
            transactions = Transaction.objects.filter(group__exact=group).filter(fusion__exact=True).delete()
            transactions = Transaction.objects.filter(group__exact=group).filter(fused__exact=True)
            for t in transactions:
                t.fused = False
                t.fused_into = None
                t.save()

            users = User.objects.filter(group__exact=group).order_by("username")

            for user in users:
                self.stdout.write(user.username)

            for creditor in users:

                transactions = Transaction.objects.filter(group__exact=group).filter(user__exact=creditor).filter(date__lte=timezone.now()-age)

                truth_table = list(product([False, True], repeat=len(users)))

                for case in truth_table:
                    self.stdout.write("Débiteurs : {}".format(case))
                    total = Decimal(0)
                    fusion = 0
                    to_fuse = list()

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
                            self.stdout.write("Transaction retenue : {} (par {})".format(transaction.name, creditor))
                            total += transaction.price
                            fusion += 1
                            to_fuse.append(transaction)

                    if fusion:

                        self.stdout.write("{} transactions fusionnées, total = {}$".format(fusion, total))

                        tf = Transaction(group=group,
                                name="Fusion",
                                description="Transactions de plus de {} jours".format(options["jours"][0]),
                                date=timezone.now()-age,
                                price=total,
                                user=creditor,
                                fused=False,
                                fusion=True,
                                )
                        tf.save()

                        for t in to_fuse:
                            t.fused = True
                            t.fused_into = tf
                            t.save()

