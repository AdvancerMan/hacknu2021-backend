from django.contrib import admin
from . import models

admin.site.register(models.CardsUser)
admin.site.register(models.CardDesign)
admin.site.register(models.Card)
admin.site.register(models.Battle)
admin.site.register(models.BattleRequest)
