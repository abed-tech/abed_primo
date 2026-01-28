from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from django.db import models

from .models import Conversation


class ConsommateurConversation(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def _utilisateur_a_acces(self, identifiant_conversation, utilisateur_id):
        return Conversation.objects.filter(pk=identifiant_conversation).filter(
            models.Q(proprietaire_id=utilisateur_id) | models.Q(demandeur_id=utilisateur_id)
        ).exists()

    async def connect(self):
        utilisateur = self.scope.get('user')
        if not utilisateur or not utilisateur.is_authenticated:
            await self.close(code=4401)
            return

        self.identifiant_conversation = (self.scope.get('url_route') or {}).get('kwargs', {}).get('identifiant_conversation')
        if not self.identifiant_conversation:
            await self.close(code=4400)
            return

        try:
            identifiant = int(self.identifiant_conversation)
        except (TypeError, ValueError):
            await self.close(code=4400)
            return

        a_acces = await self._utilisateur_a_acces(identifiant, utilisateur.id)
        if not a_acces:
            await self.close(code=4403)
            return

        self.groupe_conversation = f"conversation_{identifiant}"
        await self.channel_layer.group_add(self.groupe_conversation, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'groupe_conversation'):
            await self.channel_layer.group_discard(self.groupe_conversation, self.channel_name)

    async def message_nouveau(self, evenement):
        await self.send_json({'type': 'message', 'message': evenement.get('message')})
