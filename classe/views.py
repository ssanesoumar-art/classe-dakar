from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import KINDS, choix_formset
from .models import Choix, Exercice, Lecon, Matiere, Niveau, Quiz, Tentative


def badge(pct):
    return "Champion 🏆" if pct >= 80 else "Explorateur ⭐" if pct >= 50 else "Débutant 🌱"


def home(request):
    niveaux = Niveau.objects.annotate(
        nb_lecons=Count("lecon", distinct=True), nb_quiz=Count("quiz", distinct=True),
        nb_exos=Count("exercice", distinct=True)).order_by("ordre")
    return render(request, "home.html", {"niveaux": niveaux})


def niveau(request, code):
    n = get_object_or_404(Niveau, code=code)
    vue = request.GET.get("v") if request.GET.get("v") in ("quiz", "exercices") else "lecons"
    m = request.GET.get("m", "")
    ctx = {"niveau": n, "vue": vue, "m": m, "matieres": Matiere.objects.all(),
           "petit": n.ordre <= 1}
    if vue == "quiz":
        qs = n.quiz_set.select_related("matiere").prefetch_related("choix")
        if m:
            qs = qs.filter(matiere__code=m)
        essais = {}
        if request.user.is_authenticated:
            essais = {t.quiz_id: t for t in Tentative.objects.filter(eleve=request.user, quiz__in=qs)}
        items = [(q, essais.get(q.id)) for q in qs]
        ctx.update(items=items, total=len(items),
                   bonnes=sum(1 for _, t in items if t and t.correct))
    elif vue == "exercices":
        qs = n.exercice_set.select_related("matiere")
        if m:
            qs = qs.filter(matiere__code=m)
        ctx["exercices"] = qs
    else:
        qs = n.lecon_set.select_related("matiere")
        if m:
            qs = qs.filter(matiere__code=m)
        ctx["lecons"] = qs
    return render(request, "niveau.html", ctx)


@require_POST
def repondre(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    try:
        choix = quiz.choix.get(pk=int(request.POST.get("choix", "")))
    except (ValueError, Choix.DoesNotExist):
        return JsonResponse({"erreur": "choix invalide"}, status=400)
    bonne = quiz.choix.filter(correct=True).first()
    if request.user.is_authenticated:
        Tentative.objects.update_or_create(
            eleve=request.user, quiz=quiz, defaults={"choix": choix, "correct": choix.correct})
    return JsonResponse({"correct": choix.correct, "bonne": bonne.id if bonne else None,
                         "explication": quiz.explication})


@require_POST
@login_required
def recommencer(request, quiz_id):
    Tentative.objects.filter(eleve=request.user, quiz_id=quiz_id).delete()
    return JsonResponse({"ok": True})


@login_required
def progression(request):
    niveaux = Niveau.objects.annotate(
        nb_quiz=Count("quiz", distinct=True),
        bonnes=Count("quiz__tentative", distinct=True,
                     filter=Q(quiz__tentative__eleve=request.user, quiz__tentative__correct=True)))
    niveaux = niveaux.order_by("ordre")
    total = sum(n.nb_quiz for n in niveaux)
    bonnes = sum(n.bonnes for n in niveaux)
    for n in niveaux:
        n.pct = round(n.bonnes * 100 / n.nb_quiz) if n.nb_quiz else 0
    pct = round(bonnes * 100 / total) if total else 0
    return render(request, "progression.html",
                  {"niveaux": niveaux, "bonnes": bonnes, "pct": pct, "badge": badge(pct)})


@staff_member_required
def statistiques(request):
    quiz = (Quiz.objects.select_related("niveau", "matiere")
            .annotate(essais=Count("tentative"),
                      reussis=Count("tentative", filter=Q(tentative__correct=True)))
            .order_by("niveau__ordre", "id"))
    for q in quiz:
        q.pct = round(q.reussis * 100 / q.essais) if q.essais else None
    nb_eleves = Tentative.objects.values("eleve").distinct().count()
    return render(request, "stats.html", {"quiz": quiz, "nb_eleves": nb_eleves})


def inscription(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})


MODELES = {"lecon": Lecon, "exercice": Exercice, "quiz": Quiz}
enseignant_requis = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="login")


@enseignant_requis
def enseignant(request):
    code = request.GET.get("niveau", "")

    def liste(model):
        qs = model.objects.select_related("niveau", "matiere")
        return qs.filter(niveau__code=code) if code else qs

    return render(request, "enseignant.html", {
        "niveaux": Niveau.objects.all(), "code": code, "lecons": liste(Lecon),
        "exercices": liste(Exercice), "quiz": liste(Quiz)})


@enseignant_requis
def editer(request, kind, pk=None):
    if kind not in KINDS:
        raise Http404
    nom, Form = KINDS[kind]
    obj = get_object_or_404(MODELES[kind], pk=pk) if pk else None
    initial = {}
    if not obj and request.GET.get("niveau"):
        initial["niveau"] = Niveau.objects.filter(code=request.GET["niveau"]).first()
    form = Form(request.POST or None, instance=obj, initial=initial)
    formset = choix_formset(2 if obj else 4)(request.POST or None, instance=obj) if kind == "quiz" else None
    if request.method == "POST" and form.is_valid() and (formset is None or formset.is_valid()):
        with transaction.atomic():
            saved = form.save()
            if formset is not None:
                formset.instance = saved
                formset.save()
        messages.success(request, f"{nom} enregistré(e).")
        return redirect(f"{redirect('enseignant').url}?niveau={saved.niveau.code}")
    return render(request, "formulaire.html", {"form": form, "formset": formset, "nom": nom, "obj": obj})


@require_POST
@enseignant_requis
def supprimer(request, kind, pk):
    if kind not in MODELES:
        raise Http404
    obj = get_object_or_404(MODELES[kind], pk=pk)
    code = obj.niveau.code
    obj.delete()
    messages.success(request, "Supprimé.")
    return redirect(f"{redirect('enseignant').url}?niveau={code}")
