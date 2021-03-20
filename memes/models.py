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
    strength = models.PositiveIntegerField()
    rarity = models.PositiveIntegerField()
    design = models.ForeignKey(CardDesign, on_delete=models.PROTECT)
    owner = models.ForeignKey(CardsUser, on_delete=models.CASCADE)


class Battle(models.Model):
    battle_id = models.BigAutoField(primary_key=True)
    winner = models.ForeignKey(CardsUser, null=True, on_delete=models.PROTECT)
    first_card = models.ForeignKey(Card, on_delete=models.PROTECT,
                                   related_name='battles1')
    second_card = models.ForeignKey(Card, on_delete=models.PROTECT,
                                    related_name='battles2')

    @property
    def finished(self):
        return self.winner is None


class BattleRequest(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    battle = models.ForeignKey(Battle, null=True, blank=True, default=None,
                               on_delete=models.CASCADE,)
