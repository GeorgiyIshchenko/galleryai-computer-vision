from django.db import models
from colorfield.fields import ColorField
from django.shortcuts import reverse
from django.utils.translation import ugettext


class YoloClass(models.Model):
    name = models.CharField(max_length=50)
    photos = models.ManyToManyField(to='web.Photo', blank=True, related_name='yolo_classes')
    color = ColorField(default='#FF0000')

    class Meta:
        verbose_name = "Yolo class"
        verbose_name_plural = "Yolo classes"

    def __str__(self):
        return ugettext(self.name)

    def get_absolute_url(self):
        return reverse('yolo:index_yc', kwargs={'yc_pk': self.pk})


'''
from yolo.models import YoloClass
import random
names = open('D://GalleryAI//yolo//classes.txt').read().strip().split('\n')
for i in names:
    r = lambda: random.randint(0, 255)
    YoloClass.objects.create(name=i, color='#%02X%02X%02X' % (r(),r(),r()))
'''


class YoloObject(models.Model):
    photo_view_size = 760

    yolo_class = models.ForeignKey(YoloClass, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    accuracy = models.FloatField()
    photo = models.ForeignKey(to='web.Photo', on_delete=models.CASCADE, related_name="yolo_objects")

    def __str__(self):
        return f'{self.yolo_class}--{self.photo}'

    def get_acc(self):
        return int(self.accuracy * 100)

    def get_fs(self):
        return 20

    def get_margin_top(self):
        return int(self.get_height() / 2 - 20)

    def get_scale_factor(self):
        width = self.photo.full_image.width
        height = self.photo.full_image.height
        if width >= height:
            return YoloObject.photo_view_size / self.photo.full_image.width
        return YoloObject.photo_view_size / self.photo.full_image.height

    def get_width(self):
        return int(self.get_scale_factor() * self.width)

    def get_height(self):
        return int(self.get_scale_factor() * self.height)

    def get_x(self):
        return int(self.get_scale_factor() * self.x)

    def get_y(self):
        return int(self.get_scale_factor() * self.y)
