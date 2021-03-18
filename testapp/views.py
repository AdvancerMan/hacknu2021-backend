from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from testapp.models import TestModel
from testapp.serializers import TestSerializer


class TestView(APIView):
    def get(self, request):
        return Response('hello')


class GetAllView(APIView):
    def get(self, request):
        return Response(TestSerializer(TestModel.objects.all()).data)


class AddView(APIView):
    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=400)

        serializer.save()
        return Response({'answer': 'Success!'})
