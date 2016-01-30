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

        parser.add_argument("--days",
                dest="days",
                action="store",
                type=int,
                default=90,
                help="Fusionne les transactions de plus de X jours",
                )

        parser.add_argument("--dry-run",
                dest="dry",
                action="store_true",
                default=False,
                help="Test (ne fait aucune action)",
                )

        parser.add_argument("--reset",
                dest="reset",
                action="store_true",
                default=False,
                help="Annule toutes les fusions actuelles",
                )

        parser.add_argument("--verbose",
                dest="verbose",
                action="store_true",
                default=False,
                help="Imprime davantage de messages pendant l'exécution",
                )

    def handle(self, *args, **options):

        if options["dry"]:
            self.stdout.write("Mode test (ne modifie pas la base de données).")

        if options["reset"]:
            self.stdout.write("Annulation des fusions existantes.")

        age=timedelta(options["days"])

        groups = Group.objects.all()

        for group in groups:

            # On débute par effacer toutes les fusions précédentes
            if not options["dry"]:
                Transaction.objects.filter(group__exact=group).filter(fusion__exact=True).delete()
                transactions = Transaction.objects.filter(group__exact=group).filter(fused__exact=True)
                for t in transactions:
                    t.fused = False
                    t.fused_into = None
                    t.save()

            # Si on est en mode "reset", on passe immédiatement au groupe suivant
            if options["reset"]:
                continue

            users = User.objects.filter(group__exact=group).order_by("username")

            # Affiche les membres du groupe (débuggage, peut être retiré du script final)
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
                            if options["verbose"]:
                                self.stdout.write("Transaction retenue : {} (par {})".format(transaction.name, creditor))
                            total += transaction.price
                            fusion += 1
                            to_fuse.append(transaction)

                    # Enregistrement des modifications dans la base de données
                    if fusion and not options["dry"]:

                        self.stdout.write("{} transactions fusionnées, total = {}$".format(fusion, total))

                        tf = Transaction(group=group,
                                name="Fusion",
                                description="Transactions de plus de {} jours".format(options["days"]),
                                date=timezone.now()-age,
                                price=total,
                                user=creditor,
                                fused=False,
                                fusion=True,
                                )
                        tf.save()

                        i=0
                        for debtor in case:
                            if debtor:
                                Debtor(user=users[i], transaction=tf).save()
                            i += 1

                        for t in to_fuse:
                            t.fused = True
                            t.fused_into = tf
                            t.save()

