from django.utils.text import slugify

from .models import Utilisateur


def generer_propositions_noms_utilisateur(prenom, nom, poste_nom, nombre=5):
    base = slugify(f"{prenom}-{nom}-{poste_nom}")
    base = base.replace('-', '')
    base = base[:20] if base else 'utilisateur'

    propositions = []
    suffixe = 0

    while len(propositions) < nombre:
        candidat = base if suffixe == 0 else f"{base}{suffixe}"
        candidat = candidat[:80]

        if candidat not in propositions and not Utilisateur.objects.filter(nom_utilisateur=candidat).exists():
            propositions.append(candidat)

        suffixe += 1

    return propositions
