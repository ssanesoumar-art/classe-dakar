from django.contrib import admin

from .forms import ChoixFormSet
from .models import Choix, Exercice, Lecon, Matiere, Niveau, Quiz, Tentative


class ChoixInline(admin.TabularInline):
    model = Choix
    formset = ChoixFormSet
    extra = 4


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [ChoixInline]
    list_display = ["question", "niveau", "matiere"]
    list_filter = ["niveau", "matiere"]
    search_fields = ["question"]


@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ["titre", "niveau", "matiere", "cree"]
    list_filter = ["niveau", "matiere"]
    search_fields = ["titre", "contenu"]


@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ["titre", "niveau", "matiere", "cree"]
    list_filter = ["niveau", "matiere"]
    search_fields = ["titre", "consigne"]


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ["nom", "code", "ordre"]
    prepopulated_fields = {"code": ("nom",)}


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ["nom", "emoji", "code"]
    prepopulated_fields = {"code": ("nom",)}


@admin.register(Tentative)
class TentativeAdmin(admin.ModelAdmin):
    list_display = ["eleve", "quiz", "correct", "date"]
    list_filter = ["correct", "quiz__niveau"]
