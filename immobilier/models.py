from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone


class GestionnaireUtilisateur(BaseUserManager):
    def creer_utilisateur(self, nom_utilisateur, mot_de_passe=None, **champs_supplementaires):
        if not nom_utilisateur:
            raise ValueError("Le nom d'utilisateur est obligatoire.")

        utilisateur = self.model(nom_utilisateur=nom_utilisateur, **champs_supplementaires)
        utilisateur.set_password(mot_de_passe)
        utilisateur.full_clean()
        utilisateur.save(using=self._db)
        return utilisateur

    def creer_superutilisateur(self, nom_utilisateur, mot_de_passe=None, **champs_supplementaires):
        champs_supplementaires.setdefault('est_staff', True)
        champs_supplementaires.setdefault('est_superutilisateur', True)
        champs_supplementaires.setdefault('est_actif', True)

        if champs_supplementaires.get('est_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir est_staff=True.")
        if champs_supplementaires.get('est_superutilisateur') is not True:
            raise ValueError("Le superutilisateur doit avoir est_superutilisateur=True.")

        return self.creer_utilisateur(nom_utilisateur, mot_de_passe, **champs_supplementaires)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    prenom = models.CharField(max_length=80)
    nom = models.CharField(max_length=80)
    poste_nom = models.CharField(max_length=80)

    nom_utilisateur = models.SlugField(max_length=80, unique=True, editable=False)

    photo = models.ImageField(upload_to='photos_utilisateurs/', blank=True, null=True)

    est_actif = models.BooleanField(default=True)
    est_staff = models.BooleanField(default=False)

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    objects = GestionnaireUtilisateur()

    USERNAME_FIELD = 'nom_utilisateur'
    REQUIRED_FIELDS = ['prenom', 'nom', 'poste_nom']

    def clean(self):
        super().clean()
        if self.pk:
            ancien = Utilisateur.objects.filter(pk=self.pk).only('nom_utilisateur').first()
            if ancien and ancien.nom_utilisateur != self.nom_utilisateur:
                raise ValidationError({'nom_utilisateur': "Le nom d'utilisateur n'est pas modifiable."})

    @property
    def est_superutilisateur(self):
        return bool(self.is_superuser)

    @est_superutilisateur.setter
    def est_superutilisateur(self, valeur):
        self.is_superuser = bool(valeur)

    def __str__(self):
        return self.nom_utilisateur


class Adresse(models.Model):
    avenue = models.CharField(max_length=120)
    numero = models.CharField(max_length=20)
    quartier = models.CharField(max_length=120)
    commune = models.CharField(max_length=120)
    niveau = models.CharField(max_length=50)
    code_appartement = models.CharField(max_length=20)

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['avenue', 'numero', 'quartier', 'commune', 'niveau', 'code_appartement'],
                name='unicite_adresse_exacte',
            ),
        ]

    def __str__(self):
        return f"{self.avenue} {self.numero}, {self.quartier}, {self.commune}, niv. {self.niveau}, {self.code_appartement}"


class Publication(models.Model):
    class StatutTransaction(models.TextChoices):
        A_LOUER = 'A_LOUER', 'À louer'
        A_VENDRE = 'A_VENDRE', 'À vendre'

    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='publications')
    adresse = models.OneToOneField(Adresse, on_delete=models.PROTECT, related_name='publication')

    video = models.FileField(upload_to='videos_publications/')
    titre = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    prix = models.PositiveIntegerField()
    statut_transaction = models.CharField(max_length=20, choices=StatutTransaction.choices)
    est_disponible = models.BooleanField(default=True)

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    def clean(self):
        super().clean()
        if not self.video:
            raise ValidationError({'video': 'La vidéo est obligatoire.'})

    def __str__(self):
        return self.titre


class Conversation(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='conversations')
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='conversations_comme_proprietaire')
    demandeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='conversations_comme_demandeur')

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(proprietaire=models.F('demandeur')),
                name='conversation_proprietaire_different_demandeur',
            ),
            models.UniqueConstraint(
                fields=['publication', 'demandeur'],
                name='unicite_conversation_par_publication_et_demandeur',
            ),
        ]

    def clean(self):
        super().clean()
        if self.publication_id and self.proprietaire_id:
            if self.publication.proprietaire_id != self.proprietaire_id:
                raise ValidationError({'proprietaire': "Le propriétaire doit correspondre au propriétaire de la publication."})

    def __str__(self):
        return f"{self.publication_id} - {self.demandeur_id}"


class Message(models.Model):
    class TypeMessage(models.TextChoices):
        TEXTE = 'TEXTE', 'Texte'
        FICHIER = 'FICHIER', 'Fichier'
        VOCAL = 'VOCAL', 'Vocal'

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes')

    contenu = models.TextField(blank=True)
    fichier = models.FileField(upload_to='fichiers_messages/', blank=True, null=True)
    vocal = models.FileField(upload_to='vocaux_messages/', blank=True, null=True)

    type_message = models.CharField(max_length=10, choices=TypeMessage.choices, default=TypeMessage.TEXTE)
    est_lu = models.BooleanField(default=False)

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['date_creation']

    def clean(self):
        super().clean()
        if not self.contenu and not self.fichier and not self.vocal:
            raise ValidationError('Un message doit contenir du texte ou un fichier.')
        if self.expediteur_id and self.conversation_id:
            if self.expediteur_id not in [self.conversation.proprietaire_id, self.conversation.demandeur_id]:
                raise ValidationError({'expediteur': "L'expéditeur doit faire partie de la conversation."})

        if self.vocal and self.fichier:
            raise ValidationError('Un message ne peut pas contenir un fichier et un vocal en même temps.')

        if self.vocal:
            self.type_message = Message.TypeMessage.VOCAL
        elif self.fichier:
            self.type_message = Message.TypeMessage.FICHIER
        else:
            self.type_message = Message.TypeMessage.TEXTE

    def __str__(self):
        return f"Message {self.pk}"


class Signalement(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='signalements')
    auteur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='signalements')

    motif = models.CharField(max_length=80)
    description = models.TextField(blank=True)

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-date_creation']

    def clean(self):
        super().clean()
        self.motif = (self.motif or '').strip()
        self.description = (self.description or '').strip()
        if not self.motif:
            raise ValidationError({'motif': 'Le motif est obligatoire.'})

    def __str__(self):
        return f"Signalement {self.pk}"
