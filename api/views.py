from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework import status

from web.models import *
from django.db.models import Q
from ai.tasks import start_train, start_prediction

from .serializers import *
from .utils import check_token


class PhotoView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser,)

    def get(self, request, pk):
        photo = Photo.objects.get(id=pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data)


class PhotoDelete(APIView):

    def post(self, request, pk):
        check_token(request)
        Photo.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_200_OK)


class StartTrain(APIView):

    def post(self, request, project_pk):
        check_token(request)
        print('api_train')
        project = Project.objects.get(pk=project_pk)
        start_train.delay(project.id)
        return Response({'success': True}, status=status.HTTP_201_CREATED)


class StartPrediction(APIView):

    def post(self, request):
        user = check_token(request=request)
        start_prediction.delay(user.id)
        return Response({'success': True}, status=status.HTTP_201_CREATED)


class PhotoPostTrain(APIView):

    def post(self, request):
        print(request.data)
        user = check_token(request)
        photo_serializer = TrainSerializer(data=request.data)
        if photo_serializer.is_valid():
            photo = photo_serializer.save(user=user)
            photo.projects.add(Project.objects.get(id=request.data['project']), through_defaults={'match': request.data['match'] == 'true', 'is_ai_tag': False})
            return Response(photo_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoPostPrediction(APIView):

    def post(self, request):
        user = check_token(request)
        photo_serializer = PredictionSerializer(data=request.data)
        if photo_serializer.is_valid():
            photo = photo_serializer.save(user=user)
            for project in user.projects.all():
                photo.projects.add(project, through_defaults={'match': None, 'is_ai_tag': True})
            return Response(photo_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectsView(APIView):

    def get(self, request):
        projects = Project.objects.filter(user=request.user).order_by('created_at')
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = check_token(request=request)
        projects = Project.objects.filter(user=user).order_by('created_at')
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectView(APIView):

    def get(self, request, project_pk):
        project = Project.objects.get(pk=project_pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_pk):
        check_token(request)
        project = Project.objects.get(pk=project_pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GalleryView(APIView):
    def get(self, request):
        photos = Photo.objects.filter(user=request.user)
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = check_token(request=request)
        photos = Photo.objects.filter(user=user)
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectCreate(APIView):

    def post(self, request):
        user = check_token(request)
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDelete(APIView):

    def post(self, request, pk):
        check_token(request)
        Project.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):

    def post(self, request):
        user = check_token(request)
        serializer = UserSerializer(user)
        return Response(serializer.data)
