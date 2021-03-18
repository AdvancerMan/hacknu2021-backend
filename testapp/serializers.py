from rest_framework.serializers import ModelSerializer, Serializer,\
    SerializerMethodField

from testapp import models


class TestItemSerializer(ModelSerializer):
    class Meta:
        model = models.TestModel
        fields = ('x',)


class TestSerializer(Serializer):
    data = TestItemSerializer(many=True)

    def to_representation(self, data):
        return super(TestSerializer, self).to_representation(
            data if isinstance(data, dict) else {'data': data}
        )

    def create(self, validated_data):
        return self.fields['data'].create(validated_data['data'])
