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


class CardsCoinsSerializer(ModelSerializer):
    coins = SerializerMethodField()
    cards = SerializerMethodField()

    def get_cards(self, coins_cards):
        return CardSerializer(coins_cards[1], many=True).data

    def get_coins(self, coins_cards):
        return coins_cards[0]

    class Meta:
        model = CardsUser
        fields = ['coins', 'cards']


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
    creator = CardsUserSerializer()

    class Meta:
        model = CardDesign
        fields = ['creator', 'card_design_id', 'image_url', 'popularity']


class CardSerializer(ModelSerializer):
    card_design = SerializerMethodField()

    class Meta:
        model = Card
        fields = ['card_id', 'power', 'rarity', 'card_design']


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


class StartBattleRequestSerializer(Serializer):
    user_id = IntegerField(min_value=1)
    battle_id = IntegerField(min_value=1)
    mini_game_choice = IntegerField()

    def validate_battle_id(self, battle_id):
        battle = Battle.objects.filter(battle_id=battle_id).first()
        if battle is None:
            raise ValidationError("There is no battle with this id")
        if battle.finished:
            raise ValidationError("Battle has already been finished")
        return battle_id

    def validate_mini_game_choice(self, mini_game_choice):
        if mini_game_choice not in range(-1, 3):
            raise ValidationError("Should one of {-1, 0, 1, 2}")
        return mini_game_choice

    def validate(self, attrs):
        user_id = attrs['user_id']
        battle = Battle.objects.get(battle_id=attrs['battle_id'])
        if user_id not in [battle.first_card.owner.cards_user_id,
                           battle.second_card.owner.cards_user_id]:
            raise ValidationError("You did not join this battle")
        return attrs


class BattleResultsRequestSerializer(Serializer):
    battle_id = IntegerField(min_value=1)

    def validate_battle_id(self, battle_id):
        battle = Battle.objects.filter(battle_id=battle_id).first()
        if battle is None:
            raise ValidationError("There is no battle with this id")
        return battle_id


class BattleResultSerializer(ModelSerializer):
    winner = CardsUserSerializer()
    coins_prize = SerializerMethodField()
    power_prize = SerializerMethodField()
    card_prize = SerializerMethodField()
    delta_rating = SerializerMethodField()

    def get_coins_prize(self, battle):
        return battle.coins_prize \
            if self.context['user'] == battle.winner else 0

    def get_power_prize(self, battle):
        return (battle.first_power_prize
                if self.context['user'] == battle.first_card.owner
                else battle.second_power_prize)

    def get_card_prize(self, battle):
        return (CardSerializer(battle.card_prize).data
                if self.context['user'] == battle.winner
                   and battle.card_prize is not None
                else None)

    def get_delta_rating(self, battle):
        return (battle.first_delta_rating
                if self.context['user'] == battle.first_card.owner
                else battle.second_delta_rating)

    class Meta:
        model = Battle
        fields = ['winner', 'coins_prize', 'power_prize',
                  'card_prize', 'delta_rating']
