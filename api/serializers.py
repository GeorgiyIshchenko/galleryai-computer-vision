from rest_framework import serializers

from web.models import Photo, CustomUser, Project, PhotoProject


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username')


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=50)


class MetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhotoProject
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    meta = MetaSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'is_trained', 'photos')


class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'name', 'is_trained')


class ProjectCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('name', )


class TrainSerializer(serializers.ModelSerializer):
    meta = MetaSerializer()

    class Meta:
        model = Photo
        fields = ('image', 'device_path', 'device_uri', 'meta')


class PredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('image', 'device_path', 'device_uri')
