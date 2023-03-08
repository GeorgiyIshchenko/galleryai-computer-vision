from django.urls import path, include
from rest_framework.authtoken import views

from .views import *
from .apps import ApiConfig

app_name = ApiConfig.name

urlpatterns = [
    path('token-auth/', views.obtain_auth_token),

    path('photos/<int:pk>/', PhotoView.as_view()),
    path('photos/<int:pk>/delete', PhotoDelete.as_view()),

    path('post_photo_train', PhotoPostTrain.as_view()),
    path('post_photo_prediction', PhotoPostPrediction.as_view()),

    path('gallery', GalleryView.as_view()),

    path('projects', ProjectsView.as_view()),
    path('projects/<int:project_pk>', ProjectView.as_view()),

    path('create_project', ProjectCreate.as_view()),

    path('start_train_project/<int:project_pk>', StartTrain.as_view()),
    path('start_prediction', StartPrediction.as_view()),

    path('get_user', UserView.as_view()),
]