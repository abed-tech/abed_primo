from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Adresse, Conversation, Message, Publication, Signalement, Utilisateur


@admin.register(Utilisateur)
class AdministrationUtilisateur(UserAdmin):
    ordering = ['nom_utilisateur']
    list_display = ['nom_utilisateur', 'prenom', 'nom', 'poste_nom', 'est_staff', 'est_actif']
    list_filter = ['est_staff', 'est_actif']
    search_fields = ['nom_utilisateur', 'prenom', 'nom', 'poste_nom']

    fieldsets = (
        (None, {'fields': ('nom_utilisateur', 'password')}),
        (_('Informations personnelles'), {'fields': ('prenom', 'nom', 'poste_nom', 'photo')}),
        (_('Permissions'), {'fields': ('est_actif', 'est_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates importantes'), {'fields': ('last_login', 'date_creation')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom_utilisateur', 'prenom', 'nom', 'poste_nom', 'password1', 'password2', 'est_actif', 'est_staff'),
        }),
    )

    readonly_fields = ['nom_utilisateur', 'date_creation']


@admin.register(Adresse)
class AdministrationAdresse(admin.ModelAdmin):
    list_display = ['avenue', 'numero', 'quartier', 'commune', 'niveau', 'code_appartement', 'date_creation']
    search_fields = ['avenue', 'numero', 'quartier', 'commune', 'niveau', 'code_appartement']
    list_filter = ['commune', 'quartier']


@admin.register(Publication)
class AdministrationPublication(admin.ModelAdmin):
    list_display = ['titre', 'proprietaire', 'statut_transaction', 'est_disponible', 'prix', 'date_creation']
    search_fields = ['titre', 'proprietaire__nom_utilisateur', 'adresse__avenue', 'adresse__quartier', 'adresse__commune']
    list_filter = ['statut_transaction', 'est_disponible', 'adresse__commune', 'adresse__quartier']
    autocomplete_fields = ['proprietaire', 'adresse']


@admin.register(Conversation)
class AdministrationConversation(admin.ModelAdmin):
    list_display = ['id', 'publication', 'proprietaire', 'demandeur', 'date_creation']
    search_fields = ['publication__titre', 'proprietaire__nom_utilisateur', 'demandeur__nom_utilisateur']
    autocomplete_fields = ['publication', 'proprietaire', 'demandeur']


@admin.register(Message)
class AdministrationMessage(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'expediteur', 'date_creation']
    search_fields = ['contenu', 'expediteur__nom_utilisateur']
    autocomplete_fields = ['conversation', 'expediteur']


@admin.register(Signalement)
class AdministrationSignalement(admin.ModelAdmin):
    list_display = ['id', 'publication', 'auteur', 'motif', 'date_creation']
    search_fields = ['motif', 'description', 'publication__titre', 'auteur__nom_utilisateur']
    list_filter = ['motif', 'date_creation']
    autocomplete_fields = ['publication', 'auteur']
