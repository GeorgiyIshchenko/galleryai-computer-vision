from django.urls import path

from .views import *
from .apps import YoloConfig

app_name = YoloConfig.name

urlpatterns = [
    path('', index, name='index'),
    path('<int:yc_pk>', index, name='index_yc'),
    path('load', load, name='load'),
]