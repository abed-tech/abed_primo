from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import Adresse, Message, Publication, Signalement, Utilisateur
from .services import generer_propositions_noms_utilisateur


class FormulaireConnexion(forms.Form):
    nom_utilisateur = forms.CharField(label="Nom d'utilisateur")
    mot_de_passe = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    def clean(self):
        donnees = super().clean()
        nom_utilisateur = donnees.get('nom_utilisateur')
        mot_de_passe = donnees.get('mot_de_passe')

        if nom_utilisateur and mot_de_passe:
            utilisateur = authenticate(username=nom_utilisateur, password=mot_de_passe)
            if utilisateur is None:
                raise ValidationError("Identifiants invalides.")
            donnees['utilisateur'] = utilisateur

        return donnees


class FormulairePhotoProfil(forms.Form):
    photo = forms.ImageField(label='Photo de profil')


class FormulaireSignalement(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ['motif', 'description']

    def clean(self):
        donnees = super().clean()
        motif = (donnees.get('motif') or '').strip()
        description = (donnees.get('description') or '').strip()
        if not motif:
            raise ValidationError({'motif': 'Le motif est obligatoire.'})
        donnees['motif'] = motif
        donnees['description'] = description
        return donnees


class FormulaireInscription(forms.Form):
    prenom = forms.CharField(label='Prénom')
    nom = forms.CharField(label='Nom')
    poste_nom = forms.CharField(label='Poste-nom')

    nom_utilisateur = forms.ChoiceField(label="Nom d'utilisateur", choices=())

    mot_de_passe1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    mot_de_passe2 = forms.CharField(label='Confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prenom = (self.data.get('prenom') or self.initial.get('prenom') or '').strip()
        nom = (self.data.get('nom') or self.initial.get('nom') or '').strip()
        poste_nom = (self.data.get('poste_nom') or self.initial.get('poste_nom') or '').strip()

        if prenom and nom and poste_nom:
            propositions = generer_propositions_noms_utilisateur(prenom, nom, poste_nom)
        else:
            propositions = []

        self.fields['nom_utilisateur'].choices = [(p, p) for p in propositions]

    def clean(self):
        donnees = super().clean()
        mot_de_passe1 = donnees.get('mot_de_passe1')
        mot_de_passe2 = donnees.get('mot_de_passe2')

        if mot_de_passe1 and mot_de_passe2 and mot_de_passe1 != mot_de_passe2:
            raise ValidationError("Les mots de passe ne correspondent pas.")

        nom_utilisateur = donnees.get('nom_utilisateur')
        if nom_utilisateur and Utilisateur.objects.filter(nom_utilisateur=nom_utilisateur).exists():
            raise ValidationError("Ce nom d'utilisateur n'est plus disponible.")

        return donnees

    def enregistrer(self):
        donnees = self.cleaned_data
        utilisateur = Utilisateur.objects.creer_utilisateur(
            nom_utilisateur=donnees['nom_utilisateur'],
            mot_de_passe=donnees['mot_de_passe1'],
            prenom=donnees['prenom'],
            nom=donnees['nom'],
            poste_nom=donnees['poste_nom'],
        )
        return utilisateur


class FormulaireMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['contenu', 'fichier', 'vocal']

    def clean(self):
        donnees = super().clean()
        contenu = (donnees.get('contenu') or '').strip()
        fichier = donnees.get('fichier')
        vocal = donnees.get('vocal')
        if not contenu and not fichier and not vocal:
            raise ValidationError("Écris un message ou ajoute un fichier.")
        if fichier and vocal:
            raise ValidationError("Choisis soit un fichier soit un vocal, pas les deux.")
        return donnees


class FormulaireAdresse(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = ['avenue', 'numero', 'quartier', 'commune', 'niveau', 'code_appartement']

    def clean(self):
        donnees = super().clean()
        champs = ['avenue', 'numero', 'quartier', 'commune', 'niveau', 'code_appartement']
        for champ in champs:
            valeur = (donnees.get(champ) or '').strip()
            if not valeur:
                raise ValidationError("Tous les champs d'adresse sont obligatoires.")
            donnees[champ] = valeur
        return donnees


class FormulairePublicationBien(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['video', 'titre', 'description', 'prix', 'statut_transaction', 'est_disponible']

    def clean(self):
        donnees = super().clean()
        if not donnees.get('video'):
            raise ValidationError({'video': 'La vidéo est obligatoire.'})

        titre = (donnees.get('titre') or '').strip()
        if not titre:
            raise ValidationError({'titre': 'Le titre est obligatoire.'})
        donnees['titre'] = titre

        description = (donnees.get('description') or '').strip()
        donnees['description'] = description

        return donnees
