from django.urls import path, include

from .views import *
from .apps import WebConfig

app_name = WebConfig.name

urlpatterns = [
    path('account/', include('account.urls')),
    path('', homepage, name='homepage'),
    path('project_manager', project_manager, name='project_add'),
    path('projects/<int:pk>/edit', project_edit, name='project_edit'),
    path('projects/<int:pk>/delete', project_delete, name='project_delete'),
    path('train', photo_create_dataset, name='photo_create_dataset'),
    path('prediction', photo_load, name='photo_load'),
    path('<int:id>/delete', photo_delete, name='photo_delete'),
    path('<int:id>/', photo_view, name='photo_view'),
    path('<int:id>/od', photo_object_detection, name='photo_object_detection'),
    path('project_library/', project_library, name='projects'),
    path('project_library/<int:pk>zip_m', get_zip_project_m, name='project_zip_m'),
    path('project_library/<int:pk>zip_nm', get_zip_project_nm, name='project_zip_nm'),
    path('im/', profile_view, name='profile'),
]
