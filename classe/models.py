from django.conf import settings
from django.db import models


class Niveau(models.Model):
    code = models.SlugField(unique=True)
    nom = models.CharField(max_length=60)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre"]
        verbose_name_plural = "niveaux"

    def __str__(self):
        return self.nom


class Matiere(models.Model):
    code = models.SlugField(unique=True)
    nom = models.CharField(max_length=60)
    emoji = models.CharField(max_length=8, default="📘")

    class Meta:
        ordering = ["nom"]
        verbose_name_plural = "matières"

    def __str__(self):
        return f"{self.emoji} {self.nom}"


class Lecon(models.Model):
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    titre = models.CharField(max_length=150)
    emoji = models.CharField(max_length=8, blank=True)
    contenu = models.TextField()
    cree = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["niveau__ordre", "cree"]
        verbose_name = "leçon"

    def __str__(self):
        return f"{self.niveau} – {self.titre}"


class Quiz(models.Model):
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    explication = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["niveau__ordre", "id"]
        verbose_name_plural = "quiz"

    def __str__(self):
        return f"{self.niveau} – {self.question}"


class Choix(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="choix")
    texte = models.CharField(max_length=150)
    correct = models.BooleanField("bonne réponse", default=False)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "choix"

    def __str__(self):
        return self.texte


class Tentative(models.Model):
    eleve = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    choix = models.ForeignKey(Choix, on_delete=models.CASCADE)
    correct = models.BooleanField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["eleve", "quiz"], name="une_tentative_par_quiz")]


class Exercice(models.Model):
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    titre = models.CharField(max_length=150)
    emoji = models.CharField(max_length=8, blank=True)
    consigne = models.TextField()
    indice = models.CharField(max_length=250, blank=True)
    correction = models.TextField(blank=True)
    cree = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["niveau__ordre", "cree"]

    def __str__(self):
        return f"{self.niveau} – {self.titre}"
