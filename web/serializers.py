from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Photo, PhotoProject


class MetaSerializer(ModelSerializer):

    class Meta:
        model = PhotoProject
        fields = '__all__'


class PhotoSerializer(ModelSerializer):
    meta = MetaSerializer(many=True)

    class Meta:
        model = Photo
        fields = ('pk', 'image', 'meta')
