# Classe de Dakar (Django)

Plateforme de leçons et mini-quiz, de la moyenne section au CM2.

## Lancer en local
    python -m venv venv
    venv\Scripts\Activate.ps1        # Windows PowerShell ; Linux/Mac : source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed             # niveaux, matières, contenu d'exemple
    python manage.py createsuperuser  # compte enseignant
    python manage.py runserver

- Site : http://127.0.0.1:8000/   · Gestion du contenu (enseignant) : /admin/
- Les élèves créent un compte via « Créer un compte » ; leurs scores sont enregistrés.
- Espace enseignant : /enseignant/ (compte « équipe ») pour ajouter, modifier et supprimer leçons, exercices et quiz (quiz : au moins 2 réponses, une seule bonne). /admin/ reste disponible pour la gestion avancée.
- Statistiques de la classe (enseignant connecté) : /statistiques/
- Tests : python manage.py test

## Mise en ligne (variables d'environnement)
    DEBUG=0
    SECRET_KEY=<longue chaîne aléatoire>
    ALLOWED_HOSTS=monsite.example.com
    CSRF_TRUSTED_ORIGINS=https://monsite.example.com
Commandes de déploiement : `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py seed`
Démarrage : `gunicorn ecole.wsgi`
Sur PythonAnywhere : app web WSGI pointant vers `ecole.wsgi`, et fichiers statiques `/static/` → dossier `staticfiles`.
Pour un usage durable, remplacer SQLite par PostgreSQL (hébergeurs type Render).

## Vercel
Vercel détecte `manage.py`. SQLite ne convient pas (serverless) : ajoutez une base PostgreSQL (variable `DATABASE_URL`)
et la variable `SECRET_KEY`. Initialisez la base depuis votre PC :
    $env:DATABASE_URL="postgresql://..."      # PowerShell
    python manage.py migrate; python manage.py seed; python manage.py createsuperuser
