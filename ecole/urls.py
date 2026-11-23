from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Classe de Dakar – gestion du contenu"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("comptes/", include("django.contrib.auth.urls")),
    path("", include("classe.urls")),
]
