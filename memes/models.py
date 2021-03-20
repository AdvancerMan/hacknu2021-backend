from django.db import models
from rest_framework.exceptions import server_error
from django.contrib.auth.models import User

from hacknu.settings import IMAGE_STORAGE_KEY
import requests
import json


class CardsUser(models.Model):
    cards_user_id = models.PositiveIntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coins = models.PositiveIntegerField()
    battle_rating = models.IntegerField()
    creator_rating = models.IntegerField()

    battle_count = models.PositiveIntegerField()
    win_count = models.PositiveIntegerField()


class CardDesign(models.Model):
    card_design_id = models.PositiveIntegerField(primary_key=True)
    image_url = models.URLField()

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
    card_id = models.PositiveIntegerField(primary_key=True)
    strength = models.PositiveIntegerField()
    rarity = models.PositiveIntegerField()
    design = models.ForeignKey(CardDesign, on_delete=models.PROTECT)
    owner = models.ForeignKey(CardsUser, on_delete=models.CASCADE)


class Battle(models.Model):
    battle_id = models.PositiveIntegerField(primary_key=True)
    winner = models.ForeignKey(CardsUser, null=True, on_delete=models.PROTECT)
    first_card = models.ForeignKey(Card, on_delete=models.PROTECT,
                                   related_name='battles1')
    second_card = models.ForeignKey(Card, on_delete=models.PROTECT,
                                    related_name='battles2')

    @property
    def finished(self):
        return self.winner is None
