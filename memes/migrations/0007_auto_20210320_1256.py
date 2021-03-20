# Generated by Django 3.1.4 on 2021-03-20 12:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('memes', '0006_auto_20210320_1042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='strength',
            new_name='power',
        ),
        migrations.AddField(
            model_name='battle',
            name='card_prize',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='memes.card'),
        ),
        migrations.AddField(
            model_name='battle',
            name='coins_prize',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='first_delta_rating',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='first_power_delta',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='first_power_prize',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='second_delta_rating',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='second_power_delta',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='second_power_prize',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='cardsuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]