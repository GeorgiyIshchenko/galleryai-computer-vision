from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse, redirect

from .models import YoloClass
from web.models import Photo, Project


@login_required
def index(request, yc_pk=None):
    photos = request.user.photos.all().exclude(yolo_objects=None)
    yc = YoloClass.objects.all().order_by('name')

    current_class = 'Компьютерное зрение'

    if yc_pk is not None:
        current_class = YoloClass.objects.get(pk=yc_pk)
        photos = photos.filter(yolo_classes=current_class)

    if request.GET.get('class') and request.GET.get('class') != 'None':
        current_class = YoloClass.objects.get(pk=int(request.GET.get('class')))
        photos = photos.filter(yolo_classes=current_class)

    random_photo = None
    if photos.count():
        random_photo = photos.order_by('?')[0]

    return render(request, 'index.html', {
        'photos': photos,
        'random_photo': random_photo,
        'yc': yc,
        'current_class': current_class
    })


@login_required
def load(request):
    if request.method == "POST":
        images = request.FILES.getlist('photo_list')
        user = request.user
        for i in images:
            Photo.objects.create(image=i, user=user)
        return redirect(reverse("yolo:index"))
    return render(request, 'load.html')
