from django.db import models


class UploadImage(models.Model):
    name = models.CharField(max_length=255, default='image')
    image = models.ImageField(upload_to='images/')


class UploadVideo(models.Model):
    name = models.CharField(max_length=255, default='Video')
    video = models.FileField(upload_to='videos/')
