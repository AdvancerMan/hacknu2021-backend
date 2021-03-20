import random

from django.db import models
from rest_framework.exceptions import server_error
from django.contrib.auth.models import User

from hacknu.settings import IMAGE_STORAGE_KEY
import requests
import json


class CardsUser(models.Model):
    cards_user_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.PositiveIntegerField(default=0)
    battle_rating = models.IntegerField(default=0)
    creator_rating = models.IntegerField(default=0)

    battle_count = models.PositiveIntegerField(default=0)
    win_count = models.PositiveIntegerField(default=0)

    @property
    def creator_rank(self):
        return 'TODO'  # TODO

    @classmethod
    def register(cls, username, password):
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        cards_user = CardsUser.objects.create(user=user)
        cards_user.add_intro_reward()
        return cards_user

    def add_intro_reward(self):
        self.coins += 100
        # TODO add cards
        # self.card_set.add(
        #
        # )
        self.save()


class CardDesign(models.Model):
    card_design_id = models.BigAutoField(primary_key=True)
    image_url = models.URLField()
    popularity = models.IntegerField(choices=[
        (1, 'Обычная'),
        (2, 'Редкая'),
        (3, 'Невероятная'),
    ], default=1)

    @classmethod
    def upload_image(cls, request, image):
        response = requests.post('https://api.imgbb.com/1/upload', {
            'key': IMAGE_STORAGE_KEY,
            'image': image
        })

        if response.status_code != 200:
            server_error(request)
        return json.loads(response.text)['data']['url']


class Card(models.Model):
    card_id = models.BigAutoField(primary_key=True)
    power = models.PositiveIntegerField()
    rarity = models.PositiveIntegerField()
    design = models.ForeignKey(CardDesign, on_delete=models.PROTECT)
    owner = models.ForeignKey(CardsUser, on_delete=models.CASCADE)


class Battle(models.Model):
    battle_id = models.BigAutoField(primary_key=True)
    first_card = models.ForeignKey(Card, on_delete=models.PROTECT,
                                   related_name='battles1')
    second_card = models.ForeignKey(Card, on_delete=models.PROTECT,
                                    related_name='battles2')
    first_power_delta = models.IntegerField(default=None, null=True, blank=True)
    second_power_delta = models.IntegerField(default=None, null=True,
                                             blank=True)

    winner = models.ForeignKey(CardsUser, null=True, on_delete=models.PROTECT)
    coins_prize = models.IntegerField(default=None, null=True, blank=True)
    card_prize = models.ForeignKey(Card, on_delete=models.SET_NULL,
                                   default=None, null=True, blank=True)
    first_power_prize = models.IntegerField(default=None, null=True, blank=True)
    second_power_prize = models.IntegerField(default=None, null=True,
                                             blank=True)
    first_delta_rating = models.IntegerField(default=None, null=True,
                                             blank=True)
    second_delta_rating = models.IntegerField(default=None, null=True,
                                              blank=True)

    @property
    def finished(self):
        return self.winner is not None

    def finish(self):
        first_power = self.first_card.power + self.first_power_delta
        second_power = self.second_card.power + self.second_power_delta

        first = self.first_card.owner
        second = self.second_card.owner
        if random.randint(1, first_power + second_power) <= first_power:
            self.winner = first
        else:
            self.winner = second
        self.coins_prize = random.randint(40, 80)
        self.card_prize = None  # TODO card prize
        winner_power_prize = 50
        looser_power_prize = 10

        if self.winner == first:
            self.first_power_prize = winner_power_prize
            self.second_power_prize = looser_power_prize

            # TODO improve rating system
            self.first_delta_rating = 1
            self.second_delta_rating = -1
        else:
            self.first_power_prize = looser_power_prize
            self.second_power_prize = winner_power_prize

            self.first_delta_rating = -1
            self.second_delta_rating = 1

        self.winner.coins += self.coins_prize
        self.first_card.power += self.first_power_prize
        self.second_card.power += self.second_power_prize
        first.battle_rating += self.first_delta_rating
        second.battle_rating += self.second_delta_rating

        self.save()
        first.save()
        second.save()


class BattleRequest(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    battle = models.ForeignKey(Battle, null=True, blank=True, default=None,
                               on_delete=models.CASCADE,)
