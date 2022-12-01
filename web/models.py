from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile

from PIL import Image, ImageOps

from yolo.tasks import load_image

from rest_framework.authtoken.models import Token


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(blank=True, null=True, max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email.split('@')[0]


@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    print('пост сейв ресивер')
    if created:
        Token.objects.create(user=instance)


def gen_image_filename(instance, filename):
    return '{0}/{1}'.format(instance.user.email, filename)


def gen_image_filename_full(instance, filename):
    return '{0}/{1}'.format(instance.user.email, 'F_' + filename)


class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    image = models.ImageField(upload_to=gen_image_filename)
    full_image = models.ImageField(upload_to=gen_image_filename_full, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    has_od = models.BooleanField(default=False)
    device_path = models.CharField(max_length=250, null=True, blank=True)
    device_uri = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f'{self.pk}--{self.user}'

    def on_raw_message(body):
        print(body)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.full_image:
            full_image = ContentFile(self.image.read())
            new_picture_name = self.image.name.split("/")[-1]
            self.full_image.save(new_picture_name, full_image)
            image = Image.open(self.image.path)
            if image.width > 512 or image.height > 512:
                image.thumbnail((512, 512))
                image = ImageOps.exif_transpose(image)
                image.save(self.image.path)
        if not self.has_od:
            self.has_od = True
            super().save(*args, **kwargs)
            load_image.delay(self.id, self.full_image.path)

    def get_absolute_url(self):
        return reverse('web:photo_view', kwargs={'id': self.id})

    def url_set_match(self):
        return reverse('web:photo_change_status', kwargs={'id': self.id, 'status': 'n'})

    def url_set_not_match(self):
        return reverse('web:photo_change_status', kwargs={'id': self.id, 'status': 'b'})

    class Meta:
        ordering = ('-created_at',)


class Project(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='projects')
    photos = models.ManyToManyField(Photo, through='PhotoProject',
                                    related_name='projects')
    name = models.CharField(max_length=64, default='default', unique=True)
    is_trained = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    def get_random_photo(self):
        trained_match = self.photos.filter(Q(meta__match=True) & Q(meta__is_ai_tag=False))
        if trained_match.count():
            random_photo = trained_match.order_by('?')[0]
            return random_photo

    def last_update(self):
        return self.photos.order_by('-created_at')[0].created_at
    
    def get_zip_url(self):
        return reverse('web:project_zip', kwargs={'pk': self.id})

    def get_match(self):
        return self.photos.filter(meta__match=True)

    def get_absolute_url_edit(self):
        return reverse('web:project_edit', kwargs={'pk': self.id})

    def get_absolute_url_delete(self):
        return reverse('web:project_delete', kwargs={'pk': self.id})

    class Meta:
        ordering = ('name',)


class PhotoProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='meta')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='meta')
    is_ai_tag = models.BooleanField(null=True, blank=True)
    match = models.BooleanField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.project.name}-{self.photo.image.name}'
