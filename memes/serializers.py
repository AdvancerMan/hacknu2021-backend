import re

from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    Serializer, IntegerField, ModelSerializer
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from memes.models import Card, Battle, CardDesign, CardsUser, BattleRequest


class CardsUserSerializer(ModelSerializer):
    class Meta:
        model = CardsUser
        fields = ['cards_user_id', 'coins', 'battle_rating',
                  'creator_rating', 'creator_rank']


class AuthSerializer(TokenObtainPairSerializer):
    phone_regex = re.compile(r'\+7\d{10}')

    def validate(self, attrs):
        username = attrs[self.username_field]
        if not AuthSerializer.phone_regex.match(username):
            raise ValidationError('Username should be a phone number')

        data = super(AuthSerializer, self).validate(attrs)
        data['registered'] = False
        data['cards'] = []
        data['coins'] = 0
        data['user'] = CardsUserSerializer(
            CardsUser.objects.get(user__username=attrs[self.username_field])
        ).data
        return data


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
        fields = ['battle_id', 'first_card', 'second_card',
                  'first_player', 'second_player']


class StartFindBattleSerializer(Serializer):
    card_id = IntegerField(min_value=1)

    def validate_card_id(self, card_id):
        card = Card.objects.filter(card_id=card_id).first()
        if card is None:
            raise ValidationError("Card does not exist")

        if BattleRequest.objects.filter(card__owner=card.owner).exists():
            raise ValidationError("Can not start many battle "
                                  "requests at the same time")

        battle = Battle.objects.filter(
            Q(first_card__card_id=card_id) | Q(second_card__card_id=card_id)
        ).filter(winner__isnull=True)
        if battle.exists():
            raise ValidationError("You can not start findind battle"
                                  "if you are in another one")

        return card_id

    def get_card(self):
        return Card.objects.get(card_id=self.validated_data['card_id'])


class StopFindBattleSerializer(StartFindBattleSerializer):
    def validate_card_id(self, card_id):
        if not BattleRequest.objects.filter(card_id=card_id).exists():
            raise ValidationError("There is no battle request with this card")
        return card_id


class MatchPostRequestSerializer(Serializer):
    max_delta = IntegerField(min_value=0)
    user_id = IntegerField(min_value=1)

    def validate(self, attrs):
        user_id = attrs['user_id']
        if not BattleRequest.objects.filter(
                card__owner__cards_user_id=user_id).exists():
            raise ValidationError("There is no battle request with you")
        return attrs
