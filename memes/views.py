import json
import random

import requests
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.db.models.functions import Abs
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from hacknu.settings import IMAGE_STORAGE_KEY
from memes.models import CardsUser, BattleRequest, Battle, CardDesign
from memes.serializers import (
    AuthSerializer, CardSerializer, StartFindBattleSerializer,
    StopFindBattleSerializer, MatchPostRequestSerializer, BattleSerializer,
    CardsCoinsSerializer, StartBattleRequestSerializer,
    BattleResultsRequestSerializer, BattleResultSerializer,
    LeaderboardRequestSerializer, BattleLeaderSerializer,
    MyLeaderboardRequestSerializer, CardCreatorLeaderSerializer,
    AddLikeCardSerializer, RemoveLikeCardSerializer, CardDesignSerializer
)


class AuthView(TokenObtainPairView):
    permission_classes = []
    serializer_class = AuthSerializer

    def post(self, request, *args, **kwargs):
        try:
            return super(AuthView, self).post(request, *args, **kwargs)
        except AuthenticationFailed:
            if User.objects.filter(username=request.data['username']).exists():
                raise
            user = CardsUser.register(
                request.data['username'], request.data['password'],
                request.data.get('first_name', ''),
                request.data.get('last_name', '')
            )
            response = super(AuthView, self).post(request, *args, **kwargs)
            response.data['registered'] = True
            response.data['coins'] = user.coins
            response.data['cards'] = CardSerializer(
                user.card_set, many=True
            ).data
            return response


class EverydayRewardView(APIView):
    def post(self, request):
        result = request.user.cardsuser.try_add_everyday_reward()
        return Response(CardsCoinsSerializer(result).data)


class StartFindBattleView(APIView):
    def post(self, request):
        serializer = StartFindBattleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        BattleRequest.objects.create(
            card=serializer.get_card()
        )
        return Response()


class StopFindBattleView(APIView):
    def post(self, request):
        serializer = StopFindBattleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        BattleRequest.objects.filter(card_id=serializer.get_card().id).delete()
        return Response()


class MatchBattleView(APIView):
    def post(self, request):
        serializer = MatchPostRequestSerializer(
            data=request.data, context={'user': request.user.cardsuser}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        max_delta = serializer.data['max_delta']

        b_request = BattleRequest.objects.filter(
            card__owner=request.user.cardsuser
        ).first()

        if b_request.battle is not None:
            battle = b_request.battle
        else:
            pair_request = BattleRequest.objects.exclude(
                card=b_request.card
            ).annotate(
                delta=Abs(F('card__power') - b_request.card.power)
            ).filter(delta__lte=max_delta).order_by('delta').first()

            if pair_request is None:
                return Response({'battle': None})

            battle = Battle.objects.create(
                first_card=b_request.card,
                second_card=pair_request.card,
            )
            pair_request.battle = battle
            pair_request.save()

        b_request.delete()
        result_ser = BattleSerializer(battle)
        return result_ser.data


class StartBattleView(APIView):
    def post(self, request):
        serializer = StartBattleRequestSerializer(
            data=request.data, context={'user': request.user.cardsuser}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        battle = Battle.objects.get(battle_id=serializer.data['battle_id'])
        mini_game_choice = serializer.data['mini_game_choice']

        if mini_game_choice == -1:
            power_delta = 0
        else:
            power_delta = 1 if random.randint(1, 3) == 1 else -1
            # TODO maybe max delta depends on card power
            power_delta *= random.randint(1, 10)

        if battle.first_card.owner == request.user.cardsuser:
            battle.first_power_delta = power_delta
        else:
            battle.second_power_delta = power_delta

        if (battle.first_power_delta is not None
                and battle.second_power_delta is not None):
            battle.finish()
        else:
            battle.save()

        return Response({'power_delta': power_delta})


class BattleResultsView(APIView):
    def get(self, request):
        serializer = BattleResultsRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        battle = Battle.objects.get(battle_id=serializer.data['battle_id'])
        return Response(
            {
                'result': None if battle.winner is None
                else BattleResultSerializer(
                    battle, context={'user': request.user.cardsuser}
                ).data
            }
        )


class LeaderboardView(APIView):
    def get_leaders(self, start, count):
        if start < 0:
            count += start
            start = 0

        leaders = CardsUser.objects.order_by(
            '-battle_rating', 'cards_user_id'
        )[start:start + count]
        return Response({
            'leaders': getattr(self, 'leaders_serializer')(
                leaders, many=True
            ).data
        })

    def get(self, request):
        serializer = LeaderboardRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        start = serializer.data['start']
        count = serializer.data['count']
        return self.get_leaders(start, count)


class MyLeaderboardView(LeaderboardView):
    def get(self, request):
        serializer = MyLeaderboardRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = request.user.cardsuser
        distance = serializer.data['distance']
        ordering_field_name = getattr(self, 'ordering_field')
        ordering_field = getattr(user, ordering_field_name)
        index = CardsUser.objects.filter(
            Q(**{ordering_field_name + '__gt': ordering_field})
            | Q(**{ordering_field_name: ordering_field})
            & Q(cards_user_id__lt=user.cards_user_id)
        ).count()
        return self.get_leaders(index - distance, 2 * distance + 1)


class BattleLeaderboardView(LeaderboardView):
    leaders_serializer = BattleLeaderSerializer


class MyBattleLeaderboardView(MyLeaderboardView):
    leaders_serializer = BattleLeaderSerializer
    ordering_field = 'battle_rating'


class CreatorsLeaderboardView(LeaderboardView):
    leaders_serializer = CardCreatorLeaderSerializer


class MyCreatorsLeaderboardView(MyLeaderboardView):
    leaders_serializer = CardCreatorLeaderSerializer
    ordering_field = 'creator_rating'


class LikeCardView(APIView):
    def post(self, request):
        serializer = getattr(self, 'request_serializer')(
            data=request.data, context={'user': request.user.cardsuser}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        card_design_id = serializer.data['card_design_id']
        getattr(self, 'process_likes')(
            request,
            CardDesign.objects.get(card_design_id=card_design_id).likes
        )
        return Response()


class AddLikeCardView(LikeCardView):
    request_serializer = AddLikeCardSerializer

    def process_likes(self, request, likes):
        likes.add(request.user.cardsuser)


class RemoveLikeCardView(LikeCardView):
    request_serializer = RemoveLikeCardSerializer

    def process_likes(self, request, likes):
        likes.remove(request.user.cardsuser)


class CreateCardView(APIView):
    def post(self, request):
        image_base64 = request.data.get('image_base64')
        if image_base64 is None:
            return Response({'image_base64': 'This field is required'},
                            status=400)

        response = requests.post('https://api.imgbb.com/1/upload', {
            'key': IMAGE_STORAGE_KEY,
            'image': image_base64
        })
        imgbb_response = json.loads(response.text)

        if response.status_code != 200:
            return Response({'image_base64': [
                imgbb_response['error']['message']
            ]}, status=response.status_code)

        url = imgbb_response['data']['url']
        card_design = CardDesign.objects.create(
            creator=request.user.cardsuser, image_url=url
        )
        return Response(CardDesignSerializer(card_design).data)


class CardsView(APIView):
    def get(self, request):
        return Response(CardSerializer(request.user.cardsuser.card_set,
                                       many=True))
