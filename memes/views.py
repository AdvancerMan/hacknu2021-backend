from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from memes.models import CardsUser
from memes.serializers import AuthSerializer, CardSerializer


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
