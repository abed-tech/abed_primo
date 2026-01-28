from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .formulaires import FormulaireAdresse, FormulaireConnexion, FormulaireInscription, FormulaireMessage, FormulairePhotoProfil, FormulairePublicationBien, FormulaireSignalement
from .models import Conversation, Message, Publication, Utilisateur
from .services import generer_propositions_noms_utilisateur


@require_http_methods(['GET'])
def afficher_index(request):
    return render(request, 'index.html')


def _serialiser_message(message, utilisateur):
    return {
        'id': message.id,
        'expediteur_id': message.expediteur_id,
        'est_moi': message.expediteur_id == utilisateur.id,
        'contenu': message.contenu,
        'fichier_url': message.fichier.url if message.fichier else None,
        'vocal_url': message.vocal.url if getattr(message, 'vocal', None) else None,
        'type_message': getattr(message, 'type_message', 'TEXTE'),
        'est_lu': getattr(message, 'est_lu', True),
        'date_creation': message.date_creation.isoformat(),
    }


def _appliquer_tri_publications(publications, tri):
    tri = (tri or '').strip()
    if tri == 'prix_asc':
        return publications.order_by('prix', '-date_creation'), tri
    if tri == 'prix_desc':
        return publications.order_by('-prix', '-date_creation'), tri
    return publications.order_by('-date_creation'), 'recent'


def _parametres_sans_page(request):
    parametres = request.GET.copy()
    if 'page' in parametres:
        del parametres['page']
    return parametres.urlencode()


def _parametres_sans_cles(request, cles):
    parametres = request.GET.copy()
    for cle in cles:
        if cle in parametres:
            del parametres[cle]
    return parametres.urlencode()

def afficher_feed(request):
    tri = (request.GET.get('tri') or '').strip()
    page = (request.GET.get('page') or '1').strip()

    publications = Publication.objects.select_related('proprietaire', 'adresse')
    publications, tri = _appliquer_tri_publications(publications, tri)

    paginateur = Paginator(publications, 6)
    page_objet = paginateur.get_page(page)

    return render(
        request,
        'feed.html',
        {
            'publications': page_objet.object_list,
            'page_objet': page_objet,
            'tri': tri,
            'parametres_sans_page': _parametres_sans_page(request),
            'parametres_sans_page_et_tri': _parametres_sans_cles(request, ['page', 'tri']),
        },
    )


@require_http_methods(['GET'])
def afficher_profil_utilisateur(request, nom_utilisateur):
    utilisateur = get_object_or_404(Utilisateur, nom_utilisateur=nom_utilisateur)
    publications = Publication.objects.filter(proprietaire=utilisateur).select_related('adresse').order_by('-date_creation')
    return render(
        request,
        'profil_utilisateur.html',
        {
            'utilisateur': utilisateur,
            'publications': publications,
            'nombre_publications': publications.count(),
        },
    )


def afficher_recherche(request):
    quartier = (request.GET.get('quartier') or '').strip()
    commune = (request.GET.get('commune') or '').strip()
    statut_transaction = (request.GET.get('statut_transaction') or '').strip()
    disponibilite = (request.GET.get('disponibilite') or '').strip()

    prix_min = (request.GET.get('prix_min') or '').strip()
    prix_max = (request.GET.get('prix_max') or '').strip()
    tri = (request.GET.get('tri') or '').strip()
    page = (request.GET.get('page') or '1').strip()

    publications = Publication.objects.select_related('proprietaire', 'adresse').order_by('-date_creation')

    if quartier:
        publications = publications.filter(adresse__quartier__icontains=quartier)
    if commune:
        publications = publications.filter(adresse__commune__icontains=commune)
    if statut_transaction in [Publication.StatutTransaction.A_LOUER, Publication.StatutTransaction.A_VENDRE]:
        publications = publications.filter(statut_transaction=statut_transaction)

    if disponibilite == '1':
        publications = publications.filter(est_disponible=True)
    elif disponibilite == '0':
        publications = publications.filter(est_disponible=False)

    if prix_min.isdigit():
        publications = publications.filter(prix__gte=int(prix_min))
    if prix_max.isdigit():
        publications = publications.filter(prix__lte=int(prix_max))

    publications, tri = _appliquer_tri_publications(publications, tri)

    paginateur = Paginator(publications, 10)
    page_objet = paginateur.get_page(page)

    return render(
        request,
        'recherche.html',
        {
            'publications': page_objet.object_list,
            'page_objet': page_objet,
            'tri': tri,
            'parametres_sans_page': _parametres_sans_page(request),
            'valeurs': {
                'quartier': quartier,
                'commune': commune,
                'prix_min': prix_min,
                'prix_max': prix_max,
                'statut_transaction': statut_transaction,
                'disponibilite': disponibilite,
                'tri': tri,
            },
        },
    )


@login_required
@require_http_methods(['GET'])
def api_liste_conversations(request):
    conversations = (
        Conversation.objects
        .select_related('publication', 'proprietaire', 'demandeur')
        .filter(models.Q(proprietaire=request.user) | models.Q(demandeur=request.user))
        .order_by('-date_creation')
    )
    identifiants = [c.id for c in conversations]

    non_lus = (
        Message.objects
        .filter(conversation_id__in=identifiants, est_lu=False)
        .exclude(expediteur=request.user)
        .values('conversation_id')
        .annotate(nombre=models.Count('id'))
    )
    non_lus_par_conversation = {n['conversation_id']: n['nombre'] for n in non_lus}

    derniers = (
        Message.objects
        .filter(conversation_id__in=identifiants)
        .values('conversation_id')
        .annotate(dernier_id=models.Max('id'))
    )
    conversation_vers_dernier_id = {d['conversation_id']: d['dernier_id'] for d in derniers}
    derniers_messages = Message.objects.filter(id__in=conversation_vers_dernier_id.values()).select_related('expediteur')
    derniers_messages_par_conversation = {m.conversation_id: m for m in derniers_messages}

    resultats = []
    for c in conversations:
        dernier = derniers_messages_par_conversation.get(c.id)
        contact = c.demandeur if request.user.id == c.proprietaire_id else c.proprietaire
        resultat = {
            'conversation_id': c.id,
            'publication_id': c.publication_id,
            'contact_id': contact.id,
            'contact_nom_utilisateur': contact.nom_utilisateur,
            'contact_photo_url': contact.photo.url if contact.photo else None,
            'dernier_message': _serialiser_message(dernier, request.user) if dernier else None,
            'nombre_non_lus': non_lus_par_conversation.get(c.id, 0),
        }
        resultats.append(resultat)

    return JsonResponse({'conversations': resultats})


@login_required
@require_http_methods(['GET'])
def api_liste_messages(request, identifiant_conversation):
    conversation = get_object_or_404(
        Conversation.objects.select_related('publication', 'proprietaire', 'demandeur'),
        pk=identifiant_conversation,
    )
    if request.user.id not in [conversation.proprietaire_id, conversation.demandeur_id]:
        return JsonResponse({'detail': 'Interdit.'}, status=403)

    depuis_id = (request.GET.get('depuis_id') or '').strip()
    messages_qs = Message.objects.filter(conversation=conversation).select_related('expediteur')
    if depuis_id.isdigit():
        messages_qs = messages_qs.filter(id__gt=int(depuis_id))

    messages_liste = [_serialiser_message(m, request.user) for m in messages_qs.order_by('id')[:200]]
    return JsonResponse({'messages': messages_liste})


@login_required
@require_http_methods(['POST'])
def api_envoyer_message(request, identifiant_conversation):
    conversation = get_object_or_404(Conversation.objects.select_related('publication'), pk=identifiant_conversation)
    if request.user.id not in [conversation.proprietaire_id, conversation.demandeur_id]:
        return JsonResponse({'detail': 'Interdit.'}, status=403)

    formulaire = FormulaireMessage(request.POST or None, request.FILES or None)
    if not formulaire.is_valid():
        return JsonResponse({'detail': 'Message invalide.'}, status=400)

    message = formulaire.save(commit=False)
    message.conversation = conversation
    message.expediteur = request.user
    message.est_lu = False
    message.full_clean()
    message.save()

    message_json = _serialiser_message(message, request.user)

    canal = get_channel_layer()
    if canal is not None:
        async_to_sync(canal.group_send)(
            f"conversation_{conversation.id}",
            {
                'type': 'message_nouveau',
                'message': message_json,
            },
        )

    return JsonResponse({'message': message_json})


@login_required
@require_http_methods(['POST'])
def api_marquer_conversation_lue(request, identifiant_conversation):
    conversation = get_object_or_404(Conversation, pk=identifiant_conversation)
    if request.user.id not in [conversation.proprietaire_id, conversation.demandeur_id]:
        return JsonResponse({'detail': 'Interdit.'}, status=403)

    Message.objects.filter(conversation=conversation, est_lu=False).exclude(expediteur=request.user).update(est_lu=True)
    return JsonResponse({'ok': True})


@login_required
def afficher_publier_bien(request):
    formulaire_publication = FormulairePublicationBien(request.POST or None, request.FILES or None)
    formulaire_adresse = FormulaireAdresse(request.POST or None)

    if request.method == 'POST' and formulaire_publication.is_valid() and formulaire_adresse.is_valid():
        try:
            with transaction.atomic():
                try:
                    adresse = formulaire_adresse.save()
                except IntegrityError:
                    messages.error(request, "Cette adresse exacte existe déjà.")
                    raise

                publication = formulaire_publication.save(commit=False)
                publication.proprietaire = request.user
                publication.adresse = adresse
                publication.full_clean()
                publication.save()

            return redirect('details_publication', identifiant=publication.id)

        except IntegrityError:
            if not any(m.level_tag == 'error' for m in messages.get_messages(request)):
                messages.error(request, "Impossible de publier : doublon d'adresse.")

    return render(
        request,
        'publier_bien.html',
        {
            'formulaire_publication': formulaire_publication,
            'formulaire_adresse': formulaire_adresse,
        },
    )


def afficher_details_publication(request, identifiant):
    publication = get_object_or_404(Publication.objects.select_related('proprietaire', 'adresse'), pk=identifiant)
    formulaire_signalement = FormulaireSignalement()
    return render(request, 'details_publication.html', {'publication': publication, 'formulaire_signalement': formulaire_signalement})


@login_required
@require_http_methods(['POST'])
def signaler_publication(request, identifiant):
    publication = get_object_or_404(Publication, pk=identifiant)
    formulaire = FormulaireSignalement(request.POST)

    if formulaire.is_valid():
        signalement = formulaire.save(commit=False)
        signalement.publication = publication
        signalement.auteur = request.user if request.user.is_authenticated else None
        signalement.full_clean()
        signalement.save()
        messages.success(request, 'Signalement envoyé.')
        return redirect('details_publication', identifiant=publication.id)

    messages.error(request, 'Signalement invalide.')
    return redirect('details_publication', identifiant=publication.id)


@login_required
def afficher_profil(request):
    publications = Publication.objects.filter(proprietaire=request.user).select_related('adresse').order_by('-date_creation')

    nombre_publications = publications.count()
    nombre_conversations = Conversation.objects.filter(
        models.Q(proprietaire=request.user) | models.Q(demandeur=request.user)
    ).count()
    nombre_messages_non_lus = (
        Message.objects
        .filter(conversation__proprietaire=request.user)
        .exclude(expediteur=request.user)
        .filter(est_lu=False)
        .count()
        +
        Message.objects
        .filter(conversation__demandeur=request.user)
        .exclude(expediteur=request.user)
        .filter(est_lu=False)
        .count()
    )

    return render(
        request,
        'profil.html',
        {
            'publications': publications,
            'stats': {
                'nombre_publications': nombre_publications,
                'nombre_conversations': nombre_conversations,
                'nombre_messages_non_lus': nombre_messages_non_lus,
            },
        },
    )


@login_required
def afficher_parametres(request):
    return render(request, 'parametres.html')


@login_required
@require_http_methods(['POST'])
def modifier_photo_profil(request):
    formulaire = FormulairePhotoProfil(request.POST or None, request.FILES or None)
    if formulaire.is_valid():
        request.user.photo = formulaire.cleaned_data['photo']
        request.user.full_clean()
        request.user.save(update_fields=['photo'])
        messages.success(request, 'Photo de profil mise à jour.')
        return redirect('profil')

    messages.error(request, 'Photo de profil invalide.')
    return redirect('parametres')


@require_http_methods(['GET', 'POST'])
def afficher_connexion(request):
    if request.user.is_authenticated:
        return redirect('feed')

    next_url = (request.GET.get('next') or request.POST.get('next') or '').strip()
    formulaire = FormulaireConnexion(request.POST or None)
    if request.method == 'POST' and formulaire.is_valid():
        login(request, formulaire.cleaned_data['utilisateur'])
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('feed')

    return render(request, 'login.html', {'formulaire': formulaire, 'next': next_url})


@require_http_methods(['GET', 'POST'])
def afficher_inscription(request):
    if request.user.is_authenticated:
        return redirect('feed')

    formulaire = FormulaireInscription(request.POST or None)
    if request.method == 'POST' and formulaire.is_valid():
        utilisateur = formulaire.enregistrer()
        login(request, utilisateur)
        return redirect('feed')

    return render(request, 'inscription.html', {'formulaire': formulaire})


@require_http_methods(['GET'])
def afficher_propositions_inscription(request):
    prenom = (request.GET.get('prenom') or '').strip()
    nom = (request.GET.get('nom') or '').strip()
    poste_nom = (request.GET.get('poste_nom') or '').strip()

    if not prenom or not nom or not poste_nom:
        return JsonResponse({'propositions': []})

    propositions = generer_propositions_noms_utilisateur(prenom, nom, poste_nom)
    return JsonResponse({'propositions': propositions})


@login_required
@require_http_methods(['POST'])
def effectuer_deconnexion(request):
    logout(request)
    return redirect('connexion')


@login_required
def afficher_liste_messages(request):
    identifiant_publication_source = (request.GET.get('publication') or '').strip()
    if not identifiant_publication_source.isdigit():
        identifiant_publication_source = ''

    conversations = (
        Conversation.objects
        .select_related('publication', 'proprietaire', 'demandeur')
        .filter(models.Q(proprietaire=request.user) | models.Q(demandeur=request.user))
        .order_by('-date_creation')
    )

    identifiants = [c.id for c in conversations]
    derniers = (
        Message.objects
        .filter(conversation_id__in=identifiants)
        .values('conversation_id')
        .annotate(dernier_id=models.Max('id'))
    )
    conversation_vers_dernier_id = {d['conversation_id']: d['dernier_id'] for d in derniers}
    derniers_messages = Message.objects.filter(id__in=conversation_vers_dernier_id.values()).select_related('expediteur')
    derniers_messages_par_conversation = {m.conversation_id: m for m in derniers_messages}

    non_lus = (
        Message.objects
        .filter(conversation_id__in=identifiants, est_lu=False)
        .exclude(expediteur=request.user)
        .values('conversation_id')
        .annotate(nombre=models.Count('id'))
    )
    non_lus_par_conversation = {n['conversation_id']: n['nombre'] for n in non_lus}

    elements = []
    for c in conversations:
        dernier = derniers_messages_par_conversation.get(c.id)
        elements.append(
            {
                'conversation': c,
                'dernier_message': dernier,
                'nombre_non_lus': non_lus_par_conversation.get(c.id, 0),
            }
        )

    return render(
        request,
        'liste_messages.html',
        {
            'elements': elements,
            'identifiant_publication_source': identifiant_publication_source,
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def afficher_nouveau_message(request, identifiant_publication):
    publication = get_object_or_404(Publication.objects.select_related('proprietaire'), pk=identifiant_publication)

    if publication.proprietaire_id == request.user.id:
        messages.error(request, "Tu ne peux pas t'écrire à toi-même.")
        return redirect('details_publication', identifiant=publication.id)

    conversation, _ = Conversation.objects.get_or_create(
        publication=publication,
        proprietaire=publication.proprietaire,
        demandeur=request.user,
    )

    if Message.objects.filter(conversation=conversation).exists():
        return redirect('messages_prives', identifiant_conversation=conversation.id)

    formulaire = FormulaireMessage(request.POST or None, request.FILES or None)
    if request.method == 'POST' and formulaire.is_valid():
        message = formulaire.save(commit=False)
        message.conversation = conversation
        message.expediteur = request.user
        message.est_lu = False
        message.full_clean()
        message.save()
        return redirect('messages_prives', identifiant_conversation=conversation.id)

    return render(
        request,
        'nouveau_message.html',
        {
            'publication': publication,
            'conversation': conversation,
            'formulaire': formulaire,
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def afficher_messages_prives(request, identifiant_conversation):
    conversation = get_object_or_404(
        Conversation.objects.select_related('publication', 'proprietaire', 'demandeur'),
        pk=identifiant_conversation,
    )

    if request.user.id not in [conversation.proprietaire_id, conversation.demandeur_id]:
        return redirect('liste_messages')

    liste_messages = Message.objects.filter(conversation=conversation).select_related('expediteur')

    Message.objects.filter(conversation=conversation, est_lu=False).exclude(expediteur=request.user).update(est_lu=True)

    formulaire = FormulaireMessage(request.POST or None, request.FILES or None)
    if request.method == 'POST' and formulaire.is_valid():
        message = formulaire.save(commit=False)
        message.conversation = conversation
        message.expediteur = request.user
        message.est_lu = False
        message.full_clean()
        message.save()
        return redirect('messages_prives', identifiant_conversation=conversation.id)

    return render(
        request,
        'messages_prives.html',
        {
            'conversation': conversation,
            'publication': conversation.publication,
            'messages': liste_messages,
            'formulaire': formulaire,
        },
    )
