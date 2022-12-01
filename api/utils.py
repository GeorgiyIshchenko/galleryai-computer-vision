from rest_framework import status
from rest_framework.response import Response

from web.models import CustomUser
from .serializers import TokenSerializer


def check_token(request):
    token_serializer = TokenSerializer(data=request.data)
    if token_serializer.is_valid():

        token = token_serializer['token'].value

        try:
            user = CustomUser.objects.get(auth_token=token)
            return user
        except CustomUser.DoesNotExist:
            return Response("User does not exist")
    return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
