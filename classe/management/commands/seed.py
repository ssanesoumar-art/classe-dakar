from django.core.management.base import BaseCommand

from classe.models import Choix, Exercice, Lecon, Matiere, Niveau, Quiz

NIVEAUX = [("ms", "Moyenne section"), ("gs", "Grande section"), ("cp", "CP"), ("ce1", "CE1"),
           ("ce2", "CE2"), ("cm1", "CM1"), ("cm2", "CM2")]
MATIERES = [("fr", "Français", "📖"), ("ma", "Maths", "🔢"), ("ev", "Éveil & sciences", "🔬"),
            ("hg", "Histoire-Géo", "🌍"), ("cu", "Arts & culture", "🎨")]
LECONS = [
    ("ms", "ev", "Le baobab", "🌳", "Le baobab est un très grand arbre du Sénégal. Il garde l’eau dans son gros tronc."),
    ("ms", "ma", "Je compte jusqu’à 5", "🐟", "Comptons les poissons du port : 🐟 🐟 🐟 🐟 🐟 → cinq poissons !"),
    ("gs", "fr", "La lettre A", "🅰️", "Comme dans Ananas, Arbre, Abeille. Cherche le son [a] dans ton prénom."),
    ("cp", "ma", "Additionner", "➕", "2 + 3 = 5. Je mets les groupes ensemble et je compte le total."),
    ("ce1", "fr", "Le nom et le verbe", "✏️", "Le nom désigne une personne, un animal ou une chose : pirogue, enfant.\nLe verbe dit l’action : pêcher, courir."),
    ("ce2", "hg", "Dakar, notre capitale", "🏙️", "Dakar est la capitale du Sénégal. Elle est au bord de l’océan Atlantique, sur la presqu’île du Cap-Vert."),
    ("cm1", "ev", "Le cycle de l’eau", "💧", "L’eau s’évapore, forme des nuages, retombe en pluie, puis rejoint les fleuves comme le Sénégal et la Gambie."),
    ("cm2", "hg", "L’île de Gorée", "🏝️", "Gorée, face à Dakar, fait partie du patrimoine mondial de l’UNESCO. Elle rappelle l’histoire de la traite des esclaves."),
]
QUIZ = [
    ("ms", "ev", "Quel grand arbre voit-on au Sénégal ?", ["🌳 Le baobab", "🌲 Le sapin", "🍎 Le pommier"], 0, "Le baobab est l’arbre emblématique du Sénégal."),
    ("ms", "ma", "Combien de poissons ? 🐟🐟🐟", ["2", "3", "4"], 1, "1, 2, 3 : trois poissons !"),
    ("gs", "fr", "Quelle lettre commence « Ananas » ?", ["A", "B", "M"], 0, "Ananas commence par A."),
    ("gs", "ma", "Combien font 2 + 1 ?", ["2", "3", "4"], 1, "2 et 1 de plus, ça fait 3."),
    ("cp", "ma", "3 + 4 = ?", ["6", "7", "8"], 1, "3 + 4 = 7."),
    ("cp", "fr", "Combien de syllabes dans « ba-o-bab » ?", ["2", "3", "4"], 1, "ba · o · bab : 3 syllabes."),
    ("ce1", "fr", "Quel mot est un verbe ?", ["pirogue", "courir", "sable"], 1, "Courir exprime une action."),
    ("ce1", "ma", "12 − 5 = ?", ["6", "7", "8"], 1, "12 − 5 = 7."),
    ("ce2", "hg", "Quelle est la capitale du Sénégal ?", ["Thiès", "Saint-Louis", "Dakar", "Kaolack"], 2, "C’est Dakar."),
    ("ce2", "ma", "6 × 7 = ?", ["36", "42", "48"], 1, "6 × 7 = 42."),
    ("cm1", "ev", "Comment s’appelle le passage de l’eau liquide à la vapeur ?", ["La condensation", "L’évaporation", "La congélation"], 1, "L’eau chauffée par le soleil s’évapore."),
    ("cm1", "ma", "3 × 125 = ?", ["375", "350", "400"], 0, "125 × 3 = 375."),
    ("cm2", "hg", "Gorée est inscrite à quel patrimoine ?", ["Patrimoine mondial de l’UNESCO", "Réserve naturelle", "Parc national"], 0, "Gorée est classée UNESCO."),
    ("cm2", "ma", "Aire d’un rectangle de 8 cm sur 5 cm ?", ["13 cm²", "26 cm²", "40 cm²"], 2, "Longueur × largeur = 8 × 5 = 40 cm²."),
    ("cm2", "fr", "« Les élèves chantent » : quel est le sujet ?", ["chantent", "Les élèves", "élèves chantent"], 1, "Le sujet répond à « Qui chante ? »."),
]


EXOS = [
    ("ms", "ma", "Dessine 3 poissons", "🎨", "Dessine trois poissons dans l’eau, puis colorie-les.", "Compte avec tes doigts : 1, 2, 3.", "Trois poissons dessinés."),
    ("gs", "fr", "Cherche la lettre A", "🔎", "Entoure toutes les lettres A dans : A B A M A L.", "Il y en a plus de deux.", "Il y a 3 lettres A."),
    ("cp", "ma", "Petit problème", "➕", "Awa a 4 mangues. Sa maman lui en donne 3. Combien de mangues a Awa ?", "Mets les mangues ensemble.", "4 + 3 = 7 mangues."),
    ("ce1", "fr", "Trouve les verbes", "✏️", "Souligne les verbes : Le pêcheur lance son filet et attend les poissons.", "Cherche ce que fait le pêcheur.", "lance, attend"),
    ("ce2", "ma", "Table de 6", "🔢", "Complète : 6 × 3 = … ; 6 × 5 = … ; 6 × 8 = …", "Compte de 6 en 6.", "18 ; 30 ; 48"),
    ("cm1", "hg", "Situer Dakar", "🗺️", "Sur une carte du Sénégal, repère Dakar et dis quel océan la borde.", "Dakar est à l’ouest du pays.", "L’océan Atlantique."),
    ("cm2", "fr", "Rédaction", "📝", "Écris 5 phrases pour décrire le marché de ton quartier.", "Pense aux couleurs, aux bruits, aux odeurs.", "Réponse libre : l’enseignant corrige."),
]


class Command(BaseCommand):
    help = "Crée les niveaux, matières et un contenu d’exemple (sans doublon)."

    def handle(self, *args, **opts):
        niv = {c: Niveau.objects.get_or_create(code=c, defaults={"nom": n, "ordre": i})[0]
               for i, (c, n) in enumerate(NIVEAUX)}
        mat = {c: Matiere.objects.get_or_create(code=c, defaults={"nom": n, "emoji": e})[0]
               for c, n, e in MATIERES}
        if not (Lecon.objects.exists() or Quiz.objects.exists()):
            for n, m, t, e, c in LECONS:
                Lecon.objects.create(niveau=niv[n], matiere=mat[m], titre=t, emoji=e, contenu=c)
            for n, m, q, ch, ok, ex in QUIZ:
                quiz = Quiz.objects.create(niveau=niv[n], matiere=mat[m], question=q, explication=ex)
                Choix.objects.bulk_create([Choix(quiz=quiz, texte=t, correct=(i == ok)) for i, t in enumerate(ch)])
        if not Exercice.objects.exists():
            for n, m, t, e, c, i, k in EXOS:
                Exercice.objects.create(niveau=niv[n], matiere=mat[m], titre=t, emoji=e, consigne=c, indice=i, correction=k)
        self.stdout.write(self.style.SUCCESS("Contenu d’exemple prêt."))
