from django.contrib import admin

from .models import *

admin.site.register(CustomUser)
admin.site.register(Photo)
admin.site.register(Project)
admin.site.register(PhotoProject)
