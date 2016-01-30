# Huitcent

Mise à jour majeure du forum et des applications connexes. Essentiellement Django passe de la version 1.6 à la version 1.9, qui élimine plusieurs fonctions désuètes, et les applications vont abandonner Dajax et Dajaxice.

Les fonctions seront remplacées par du javascript, lorsque possible, et des requêtes standard (GET/POST) autrement.

## Statut

- J'ai temporairement désactivé la liste de tâches. Je ne suis pas sûr que ça vaille la peine de la recréer, je vais demander à Chantale si elle l'utilise vraiment;
- Je suis rendu à ajouter un --dry-run à ma commande de fusion, et à tester avec les données réelles du forum;
- Ensuite il faudra l'intégrer aux templates et aux vues dans views.py.

## Pour la migration de finance

J'ai eu plusieurs problèmes avec la migration de la base de données, à cause de l'application finance. Finalement ce que j'ai fait c'est de modifier manuellement la base de données précédente, puis de faire la migration manuellement :

    $ sqlite3 db.sqlite3
    > ALTER TABLE "finance_transaction" ADD COLUMN "fused_into_id" integer NULL REFERENCES "finance_transactions" ("id");
    > ALTER TABLE "finance_transaction" ADD COLUMN "fusion" bool NOT NULL DEFAULT 0;
    > CREATE INDEX "finance_transaction_0bf4e065" ON "finance_transaction" ("fused_into_id");
    > .quit
    $ python manage.py makemigrations
    $ python manage.py migrate

Ce que j'ai constaté par la suite c'est que j'ai probablement fait une migration alors que mon modèle de Transaction dans finance/models.py était mal défini. Je crois donc que je pourrais simplement effacer les migrations enregistrées dans finance/migrations/* et que la migration fonctionnerait alors très bien.
