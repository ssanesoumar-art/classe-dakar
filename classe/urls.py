from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("niveau/<slug:code>/", views.niveau, name="niveau"),
    path("quiz/<int:quiz_id>/repondre/", views.repondre, name="repondre"),
    path("quiz/<int:quiz_id>/recommencer/", views.recommencer, name="recommencer"),
    path("progression/", views.progression, name="progression"),
    path("statistiques/", views.statistiques, name="statistiques"),
    path("enseignant/", views.enseignant, name="enseignant"),
    path("enseignant/<str:kind>/ajouter/", views.editer, name="ajouter"),
    path("enseignant/<str:kind>/<int:pk>/modifier/", views.editer, name="modifier"),
    path("enseignant/<str:kind>/<int:pk>/supprimer/", views.supprimer, name="supprimer"),
    path("inscription/", views.inscription, name="signup"),
]
