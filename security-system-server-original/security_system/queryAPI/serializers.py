from rest_framework import serializers

from queryAPI.models import QueryAPI


class QueryAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryAPI
        fields = ('id', 'code', 'msg', 'name', 'country', 'province', 'label')
