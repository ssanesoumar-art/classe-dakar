from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Choix, Exercice, Lecon, Quiz


class ChoixFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        valides = [
            f.cleaned_data for f in self.forms
            if getattr(f, "cleaned_data", None)
            and not f.cleaned_data.get("DELETE") and f.cleaned_data.get("texte")
        ]
        if len(valides) < 2:
            raise forms.ValidationError("Ajoutez au moins 2 réponses.")
        if sum(1 for d in valides if d.get("correct")) != 1:
            raise forms.ValidationError("Cochez exactement une bonne réponse.")


class LeconForm(forms.ModelForm):
    class Meta:
        model = Lecon
        fields = ["niveau", "matiere", "emoji", "titre", "contenu"]
        labels = {"matiere": "Matière", "emoji": "Emoji (facultatif)", "titre": "Titre",
                  "contenu": "Contenu de la leçon"}
        widgets = {"contenu": forms.Textarea(attrs={"rows": 8})}


class ExerciceForm(forms.ModelForm):
    class Meta:
        model = Exercice
        fields = ["niveau", "matiere", "emoji", "titre", "consigne", "indice", "correction"]
        labels = {"matiere": "Matière", "emoji": "Emoji (facultatif)", "titre": "Titre",
                  "consigne": "Consigne de l’exercice", "indice": "Indice (facultatif)",
                  "correction": "Correction (facultatif, visible via un bouton)"}
        widgets = {"consigne": forms.Textarea(attrs={"rows": 5}),
                   "correction": forms.Textarea(attrs={"rows": 4})}


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["niveau", "matiere", "question", "explication"]
        labels = {"matiere": "Matière", "question": "Question",
                  "explication": "Explication affichée après la réponse (facultatif)"}


def choix_formset(extra):
    return inlineformset_factory(Quiz, Choix, formset=ChoixFormSet,
                                 fields=["texte", "correct"], extra=extra, can_delete=True)


KINDS = {"lecon": ("Leçon", LeconForm), "exercice": ("Exercice", ExerciceForm), "quiz": ("Quiz", QuizForm)}
