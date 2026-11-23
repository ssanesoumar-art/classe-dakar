from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Exercice, Lecon, Matiere, Niveau, Quiz, Tentative


class PlateformeTests(TestCase):
    def setUp(self):
        call_command("seed", verbosity=0)

    def test_pages_publiques(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("niveau", args=["cp"]) + "?v=quiz").status_code, 200)
        self.assertEqual(self.client.get(reverse("niveau", args=["cm2"])).status_code, 200)

    def test_reponse_enregistree(self):
        u = User.objects.create_user("awa", password="x12345678")
        self.client.force_login(u)
        q = Quiz.objects.get(question="3 + 4 = ?")
        bon = q.choix.get(correct=True)
        r = self.client.post(reverse("repondre", args=[q.id]), {"choix": bon.id})
        self.assertTrue(r.json()["correct"])
        self.assertTrue(Tentative.objects.get(eleve=u, quiz=q).correct)
        self.assertEqual(self.client.get(reverse("progression")).status_code, 200)

    def test_acces_reserves(self):
        self.assertEqual(self.client.get(reverse("progression")).status_code, 302)
        self.assertEqual(self.client.get(reverse("statistiques")).status_code, 302)
        q = Quiz.objects.first()
        r = self.client.post(reverse("repondre", args=[q.id]), {"choix": "abc"})
        self.assertEqual(r.status_code, 400)

    def test_espace_enseignant(self):
        self.assertEqual(self.client.get(reverse("enseignant")).status_code, 302)
        eleve = User.objects.create_user("eleve", password="x12345678")
        self.client.force_login(eleve)
        self.assertEqual(self.client.get(reverse("enseignant")).status_code, 302)
        prof = User.objects.create_user("prof", password="x12345678", is_staff=True)
        self.client.force_login(prof)
        self.assertEqual(self.client.get(reverse("enseignant") + "?niveau=cp").status_code, 200)
        base = {"niveau": Niveau.objects.get(code="cp").id, "matiere": Matiere.objects.get(code="ma").id}
        r = self.client.post(reverse("ajouter", args=["lecon"]),
                             {**base, "emoji": "🧮", "titre": "Soustraire", "contenu": "5 - 2 = 3"})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Lecon.objects.filter(titre="Soustraire").exists())
        r = self.client.post(reverse("ajouter", args=["exercice"]),
                             {**base, "titre": "Soustraction", "consigne": "7 - 4 = ?", "correction": "3"})
        self.assertEqual(r.status_code, 302)
        ex = Exercice.objects.get(titre="Soustraction")
        page = self.client.get(reverse("niveau", args=["cp"]) + "?v=exercices")
        self.assertContains(page, "Soustraction")
        fs = {"choix-TOTAL_FORMS": "4", "choix-INITIAL_FORMS": "0", "choix-MIN_NUM_FORMS": "0",
              "choix-MAX_NUM_FORMS": "1000", "choix-0-texte": "2", "choix-1-texte": "3",
              "choix-1-correct": "on", "choix-2-texte": "4"}
        r = self.client.post(reverse("ajouter", args=["quiz"]), {**base, "question": "5 - 2 ?", **fs})
        self.assertEqual(r.status_code, 302)
        q = Quiz.objects.get(question="5 - 2 ?")
        self.assertEqual(q.choix.count(), 3)
        self.assertEqual(q.choix.get(correct=True).texte, "3")
        # un seul choix -> refusé
        bad = {**base, "question": "Refusé ?", **fs, "choix-2-texte": "", "choix-1-texte": ""}
        self.assertEqual(self.client.post(reverse("ajouter", args=["quiz"]), bad).status_code, 200)
        self.assertFalse(Quiz.objects.filter(question="Refusé ?").exists())
        self.assertEqual(self.client.post(reverse("supprimer", args=["exercice", ex.pk])).status_code, 302)
        self.assertFalse(Exercice.objects.filter(pk=ex.pk).exists())

    def test_ordre_des_niveaux(self):
        r = self.client.get(reverse("home"))
        noms = [n.code for n in r.context["niveaux"]]
        self.assertEqual(noms, ["ms", "gs", "cp", "ce1", "ce2", "cm1", "cm2"])
