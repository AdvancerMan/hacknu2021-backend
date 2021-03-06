# Generated by Django 3.1.4 on 2021-03-20 07:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CardDesign',
            fields=[
                ('card_design_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('image_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='CardsUser',
            fields=[
                ('cards_user_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('coins', models.PositiveIntegerField()),
                ('battle_rating', models.IntegerField()),
                ('creator_rating', models.IntegerField()),
                ('battle_count', models.PositiveIntegerField()),
                ('win_count', models.PositiveIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('card_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('strength', models.PositiveIntegerField()),
                ('rarity', models.PositiveIntegerField()),
                ('design', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='memes.carddesign')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memes.cardsuser')),
            ],
        ),
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('battle_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('first_card', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='battles1', to='memes.card')),
                ('second_card', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='battles2', to='memes.card')),
                ('winner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='memes.cardsuser')),
            ],
        ),
    ]
