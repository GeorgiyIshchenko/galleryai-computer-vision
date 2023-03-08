import zipfile
import io

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.generics import get_object_or_404
from django.db import IntegrityError

from .forms import *

from .models import *
from yolo.models import YoloClass

from ai.tasks import *


@login_required
def homepage(request):
    if request.user.is_authenticated:
        user = request.user
        if user.projects.count():
            projects = user.projects.all().order_by('created_at')
            project = request.GET.get('project') if request.GET.get('project') != 'None' else None
            if project:
                project = projects.get(pk=int(request.GET.get('project')))
            else:
                try:
                    project = Project.objects.get(id=request.session['project_id'])
                except KeyError:
                    project = None
                except Project.DoesNotExist:
                    project = None

            if request.method == 'POST':
                if request.POST['type'] == 'prediction':
                    if "Not Match" in request.POST['project']:
                        for photo in project.photos.all():
                            meta = PhotoProject.objects.get(photo=photo, project=project)
                            if meta.is_ai_tag is True and meta.match is False:
                                photo.delete()
                    else:
                        for photo in project.photos.all():
                            meta = PhotoProject.objects.get(photo=photo, project=project)
                            if meta.is_ai_tag is True and meta.match is True:
                                photo.delete()
                else:
                    if "Not Match" in request.POST['project']:
                        for photo in project.photos.all():
                            meta = PhotoProject.objects.get(photo=photo, project=project)
                            if meta.is_ai_tag is False and meta.match is False:
                                photo.delete()
                    else:
                        for photo in project.photos.all():
                            meta = PhotoProject.objects.get(photo=photo, project=project)
                            if meta.is_ai_tag is False and meta.match is True:
                                photo.delete()
            if project is not None:
                match = [{'photo': photo, 'meta': photo.meta.get(project_id=project.id)} for photo in
                         project.photos.filter(Q(meta__score__gte=project.threshold) & Q(meta__is_ai_tag=True))]
                not_match = [{'photo': photo, 'meta': photo.meta.get(project_id=project.id)} for photo in
                             project.photos.filter(Q(meta__score__lt=project.threshold) & Q(meta__is_ai_tag=True))]
                trained_match = project.photos.filter(Q(meta__match=True) & Q(meta__is_ai_tag=False))
                trained_not_match = project.photos.filter(Q(meta__match=False) & Q(meta__is_ai_tag=False))

                random_photo = None
                size = len(trained_match)
                if size > 0:
                    random_photo = trained_match.order_by('?')[0]
                data = {f"Match ({len(match)})": {"color": "white", "text": "dark", "photos": match, },
                        f"Not match ({len(not_match)})": {"color": "dark", "text": "white", "photos": not_match,
                                                          }, }
                data_trained = {
                    f"Match ({len(trained_match)})": {"color": "white", "text": "dark",
                                                      "photos": trained_match, },
                    f"Not match ({len(trained_not_match)})": {"color": "dark", "text": "white",
                                                              "photos": trained_not_match, }, }
                return render(request, 'homepage.html',
                              {'data': data, 'data_trained': data_trained, 'dropdown': True, 'projects': projects,
                               'current_project': project, 'random_photo': random_photo})

            gallery = request.user.photos.all()

            random_photo = None
            if gallery.count():
                random_photo = gallery.order_by('?')[0]

            return render(request, 'homepage.html',
                          {'gallery': gallery, 'dropdown': True, 'projects': projects,
                           'current_project': project, 'random_photo': random_photo})
        return render(request, 'homepage.html', {'dropdown': True, 'add_project': True})
    return render(request, 'homepage.html')


@login_required
def project_manager(request):
    projects = request.user.projects.all()
    projects_cv = YoloClass.objects.all()
    if request.method == 'POST':
        user = request.user
        project_name = request.POST.get('project_name')
        try:
            new_project = Project.objects.create(user=user, name=project_name)
            new_project.save()
        except IntegrityError:
            print('ПРОЕКТ С ТАКИМ ИМЕНЕМ УЖЕ СУЩЕСТВУЕТ')
    return render(request, 'project_manager.html', {'projects': projects, 'projects_cv': projects_cv})


def project_library(request):
    projects = [i for i in Project.objects.all() if i.photos.count()]
    return render(request, 'projects.html', {'projects': projects})


def get_zip(project, photos):
    filenames = []
    for photo in photos:
        url = ('C:/Users/idmit/GalleryAI' + photo.image.url).split('%40')
        url = url[0] + "@" + url[1]
        print(url)
        filenames.append(url)

    zip_subdir = project.name
    zip_filename = "%s.zip" % zip_subdir

    s = io.BytesIO()

    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


def get_zip_project_m(request, pk):
    project = Project.objects.get(pk=pk)
    return get_zip(project, project.get_match())


def get_zip_project_nm(request, pk):
    project = Project.objects.get(pk=pk)
    return get_zip(project, project.get_not_match())


@login_required
def project_edit(request, pk):
    if request.method == 'POST':
        project = Project.objects.get(pk=pk)
        project.name = request.POST.get('project_name', project.name)
        project.threshold = request.POST.get('threshold', project.threshold)
        project.save()
        return redirect(reverse('web:project_add'))


@login_required
def project_delete(request, pk):
    project = Project.objects.get(pk=pk)
    project.delete()
    return redirect(reverse('web:project_add'))


@login_required
def photo_view(request, id):
    photo = get_object_or_404(Photo, id=id)
    photo_objects = photo.yolo_objects.all()
    if request.method == "POST":
        photo.match = (request.POST['match'] == "True")
        photo.is_ai_tag = False
        # start_train.delay(photo.project.id)
        photo.save()
    return render(request, 'photo_view.html', {'photo': photo, 'photo_objects': photo_objects})


@login_required
def photo_delete(request, id):
    photo = get_object_or_404(Photo, id=id)
    photo.delete()
    return redirect('/')


@login_required
def photo_load(request):
    if request.method == "POST":
        photos = request.FILES.getlist('photos')
        projects = Project.objects.filter(
            id__in=request.POST.getlist('projects', request.user.projects.filter(is_trained=True)))
        for i in photos:
            photo = Photo.objects.create(image=i, user=request.user)
            for project in projects:
                if project not in photo.projects.all():
                    photo.projects.add(project, through_defaults={'match': None, 'is_ai_tag': True})
        photo_select = [Photo.objects.get(id=int(i)) for i in request.POST.getlist('photo_select')]
        for photo in photo_select:
            for project in projects:
                if project in photo.projects.all():
                    meta = photo.meta.get(project=project)
                    meta.match = None
                    meta.is_ai_tag = True
                    meta.save()
                else:
                    photo.projects.add(project, through_defaults={'match': None, 'is_ai_tag': True})
        start_prediction.delay(request.user.id)
        return redirect('/')
    projects = request.user.projects.filter(is_trained=True)

    photos = request.user.photos.all().order_by('-id')

    return render(request, 'photo_prediction.html',
                  {'projects': projects, 'photos': photos, 'select_height': photos.count() * 100 + 50})


@login_required
def photo_create_dataset(request):
    if request.method == "POST":
        project = Project.objects.get(pk=int(request.POST.get('project')))
        match = request.FILES.getlist('match')
        doesnt_match = request.FILES.getlist('doesnt_match')
        pm = [Photo.objects.get(id=int(i)) for i in request.POST.getlist('photo_select_m')]
        pnm = [Photo.objects.get(id=int(i)) for i in request.POST.getlist('photo_select_nm')]

        for i in match:
            photo = Photo.objects.create(image=i, user=request.user)
            photo.projects.add(project, through_defaults={'match': True, 'is_ai_tag': False})

        for photo in pm:
            if project in photo.projects.all():
                meta = photo.meta.get(project=project)
                meta.match = True
                meta.is_ai_tag = False
                meta.save()
            else:
                photo.projects.add(project, through_defaults={'match': True, 'is_ai_tag': False})

        for i in doesnt_match:
            photo = Photo.objects.create(image=i, user=request.user)
            photo.projects.add(project, through_defaults={'match': False, 'is_ai_tag': False})

        for photo in pnm:
            if project in photo.projects.all():
                meta = photo.meta.get(project=project)
                meta.match = False
                meta.is_ai_tag = False
                meta.save()
            else:
                photo.projects.add(project, through_defaults={'match': False, 'is_ai_tag': False})

        start_train.delay(project.id)
        return redirect('/')
    projects = request.user.projects.all()
    current_project = None
    if projects:
        current_project = projects[0]
    if request.GET.get('project_id'):
        current_project = projects.get(id=request.GET['project_id'])
    form = DataSetCreationForm()
    photos = request.user.photos.all().order_by('-id')
    return render(request, 'photo_create_dataset.html',
                  {'projects': projects, 'form': form, 'current_project': current_project, 'photos': photos,
                   'select_height': photos.count() * 100 + 50})


@login_required
def photo_object_detection(request, id):
    photo = Photo.objects.get(id=id)
    photo_objects = photo.yolo_objects.all()
    return render(request, 'photo_object_detection.html', {
        'photo': photo,
        'photo_objects': photo_objects,
    })


@login_required
def profile_view(request):
    return render(request, 'profile_view.html')
