from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.functions import Abs
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView


from memes.models import CardsUser, BattleRequest, Battle
from memes.serializers import (
    AuthSerializer, CardSerializer, StartFindBattleSerializer,
    StopFindBattleSerializer,
    MatchPostRequestSerializer, BattleSerializer, CardsCoinsSerializer
)



class AuthView(TokenObtainPairView):
    serializer_class = AuthSerializer

    def post(self, request, *args, **kwargs):
        try:
            return super(AuthView, self).post(request, *args, **kwargs)
        except AuthenticationFailed:
            if User.objects.filter(username=request.data['username']).exists():
                raise
            user = CardsUser.register(request.data['username'],
                                      request.data['password'])
            response = super(AuthView, self).post(request, *args, **kwargs)
            response.data['registered'] = True
            response.data['coins'] = user.coins
            response.data['cards'] = CardSerializer(
                user.card_set, many=True
            ).data
            return response

class EverydayRewardView(APIView):
    def post(self):
        serializer = CardsCoinsSerializer()
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        CardsUser.everyday_login_reward()
            


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
        serializer = MatchPostRequestSerializer(data={
            'user_id': request.user.cardsuser.cards_user_id, **request.data
        })
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
                delta=Abs(F('card__strength') - b_request.card.strength)
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

