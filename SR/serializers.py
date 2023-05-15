from rest_framework import serializers
from .models import UploadImage, UploadVideo


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadImage
        fields = ('name', 'image')


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadVideo
        fields = ('name', 'video')
