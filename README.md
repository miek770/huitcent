# Huitcent

Mise à jour majeure du forum et des applications connexes. Essentiellement Django a passé de la version 1.6 à la version 1.9, qui élimine plusieurs fonctions désuètes, et les applications ont abandonneé Dajax et Dajaxice. Les fonctions ont été remplacées par du javascript, lorsque possible, et des requêtes standard (GET/POST) autrement.

Maintenant rendu à Django 1.11.2.

## À faire

- Transférer la base de données sur Postgresql sur le odroid.

## Mise à jour de Django

Suivre les instructions de Django pour la version à mettre à jour. Toujours tester la migration sur le site de développement avant du site de production. Pour mettre à jour le site de production, exécuter (idéalement préciser la version de Django) :

    cd /srv/http/huitcent
    sudo systemctl stop forum
    sudo su html
    source bin/activate
    cd huitcent
    python -Wall manage.py test
    pip install Django==1.11.3
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic

### Pour la migration de finance

J'ai eu plusieurs problèmes avec la migration de la base de données, à cause de l'application finance. Finalement ce que j'ai fait c'est de modifier manuellement la base de données précédente, puis de faire la migration manuellement :

    $ sqlite3 db.sqlite3
    > ALTER TABLE "finance_transaction" ADD COLUMN "fused_into_id" integer NULL REFERENCES "finance_transactions" ("id");
    > ALTER TABLE "finance_transaction" ADD COLUMN "fusion" bool NOT NULL DEFAULT 0;
    > CREATE INDEX "finance_transaction_0bf4e065" ON "finance_transaction" ("fused_into_id");
    > .quit
    $ python manage.py makemigrations
    $ python manage.py migrate

Ce que j'ai constaté par la suite c'est que j'ai probablement fait une migration alors que mon modèle de Transaction dans finance/models.py était mal défini. Je crois donc que je pourrais simplement effacer les migrations enregistrées dans finance/migrations et que la migration fonctionnerait alors très bien.
