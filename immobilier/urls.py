from django.urls import path

from . import vues

urlpatterns = [
    path('', vues.afficher_index, name='index'),
    path('fil/', vues.afficher_feed, name='feed'),
    path('recherche/', vues.afficher_recherche, name='recherche'),
    path('publier/', vues.afficher_publier_bien, name='publier_bien'),
    path('publication/<int:identifiant>/', vues.afficher_details_publication, name='details_publication'),
    path('publication/<int:identifiant>/signaler/', vues.signaler_publication, name='signaler_publication'),
    path('profil/', vues.afficher_profil, name='profil'),
    path('utilisateur/<slug:nom_utilisateur>/', vues.afficher_profil_utilisateur, name='profil_utilisateur'),
    path('parametres/', vues.afficher_parametres, name='parametres'),
    path('parametres/photo/', vues.modifier_photo_profil, name='modifier_photo_profil'),
    path('connexion/', vues.afficher_connexion, name='connexion'),
    path('inscription/', vues.afficher_inscription, name='inscription'),
    path('inscription/propositions/', vues.afficher_propositions_inscription, name='propositions_inscription'),
    path('deconnexion/', vues.effectuer_deconnexion, name='deconnexion'),
    path('messages/', vues.afficher_liste_messages, name='liste_messages'),
    path('messages/nouveau/<int:identifiant_publication>/', vues.afficher_nouveau_message, name='nouveau_message'),
    path('messages/conversation/<int:identifiant_conversation>/', vues.afficher_messages_prives, name='messages_prives'),

    path('api/messages/conversations/', vues.api_liste_conversations, name='api_liste_conversations'),
    path('api/messages/conversation/<int:identifiant_conversation>/', vues.api_liste_messages, name='api_liste_messages'),
    path('api/messages/conversation/<int:identifiant_conversation>/envoyer/', vues.api_envoyer_message, name='api_envoyer_message'),
    path('api/messages/conversation/<int:identifiant_conversation>/marquer_lu/', vues.api_marquer_conversation_lue, name='api_marquer_conversation_lue'),
]
