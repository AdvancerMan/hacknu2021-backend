from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    Serializer, IntegerField, ModelSerializer
)

from memes.models import Card, Battle, CardDesign, CardsUser


class CardsUserSerializer(ModelSerializer):
    class Meta:
        model = CardsUser
        fields = ['user_id', 'coins', 'battle_rating',
                  'creator_rating', 'creator_rank']


class CardDesignSerializer(ModelSerializer):
    class Meta:
        model = CardDesign
        fields = ['card_design_id', 'image_url', 'popularity']


class CardSerializer(ModelSerializer):
    card_design = SerializerMethodField()

    class Meta:
        model = Card
        fields = ['card_id', 'strength', 'rarity', 'card_design']


class BattleSerializer(ModelSerializer):
    first_card = CardSerializer()
    second_card = CardSerializer()
    first_player = SerializerMethodField()
    second_player = SerializerMethodField()

    def get_first_player(self, battle):
        return CardsUserSerializer(battle.first_card.owner).data

    def get_second_player(self, battle):
        return CardsUserSerializer(battle.second_card.owner).data

    class Meta:
        model = Battle
        fields = ['battle_id', 'first_card', 'second_card']


class CardIdSerializer(Serializer):
    card_id = IntegerField(min_value=1)

    def validate_card_id(self, card_id):
        if not Card.objects.filter(card_id=card_id).exists():
            raise ValidationError("Card does not exist")
        return card_id

    def get_card(self):
        return Card.objects.get(card_id=self.card_id)


class MatchPostRequestSerializer(Serializer):
    max_delta = IntegerField(min_value=0)
