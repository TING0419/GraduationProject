from django.contrib import admin
from .models import UploadImage, UploadVideo


admin.site.register(UploadImage)
admin.site.register(UploadVideo)
