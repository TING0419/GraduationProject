from django.shortcuts import render, HttpResponse
from django.contrib import messages

# from django.views import View
from rest_framework.views import APIView, View
from rest_framework.response import Response
from .models import UploadImage, UploadVideo
from .forms import VideoForm
from .serializers import ImageSerializer, VideoSerializer
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import ImageForm, VideoForm
import io

import torch
import torch.nn as nn
from torchvision import datasets
import torchvision.models as models
import torchvision.transforms as transforms
from torch import optim
from collections import OrderedDict
from PIL import Image
import os
import cv2
import numpy as np
import torch

from . import imgproc
from . import config
from .model import SRCNN


class ImageView(APIView):
    def get(self, request):
        images = UploadImage.objects.all()
        serializer = ImageSerializer(instance=images, many=True)
        return HttpResponse(serializer.data)

    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        print(serializer.is_valid())
        if serializer.is_valid():
            image = UploadImage.objects.create(**serializer.validated_data)
            ser = ImageSerializer(instance=image, many=False)
            return Response(ser.data)
        else:
            return Response(serializer.errors)


class ImageDetailView(APIView):
    def get(self, request, id):
        image = UploadImage.objects.get(pk=id)
        serializer = ImageSerializer(instance=image, many=False)
        return Response(serializer.data['image'])

    def delete(self, request, id):
        UploadImage.objects.get(pk=id).delete()
        return Response()


class SRView(APIView):
    def get(self, request):
        return render(request, 'index.html', {})

    def post(self, request):
        model = SRCNN().to(device=config.device, memory_format=torch.channels_last)
        checkpoint = torch.load(config.model_path, map_location=lambda storage, loc: storage)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        model.half()
        # image processing
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            image = UploadImage.objects.create(**serializer.validated_data)
            print(image)
            ser = ImageSerializer(instance=image, many=False)
        else:
            return Response(serializer.errors)
        image_path = "./media" + ser.data['image']
        lr_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0
        hr_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0

        lr_image = imgproc.image_resize(lr_image, 1 / config.upscale_factor)
        lr_image = imgproc.image_resize(lr_image, config.upscale_factor)

        lr_y_image = imgproc.bgr2ycbcr(lr_image, True)
        hr_y_image = imgproc.bgr2ycbcr(hr_image, True)

        hr_ycbcr_image = imgproc.bgr2ycbcr(hr_image, False)
        _, hr_cb_image, hr_cr_image = cv2.split(hr_ycbcr_image)

        lr_y_tensor = imgproc.image2tensor(lr_y_image, False, True).unsqueeze_(0)
        hr_y_tensor = imgproc.image2tensor(hr_y_image, False, True).unsqueeze_(0)

        lr_y_tensor = lr_y_tensor.to(device=config.device, memory_format=torch.channels_last, non_blocking=True)
        hr_y_tensor = hr_y_tensor.to(device=config.device, memory_format=torch.channels_last, non_blocking=True)

        with torch.no_grad():
            sr_y_tensor = model(lr_y_tensor).clamp_(0, 1.0)

        sr_y_image = imgproc.tensor2image(sr_y_tensor, False, True)
        sr_y_image = sr_y_image.astype(np.float32) / 255.0
        sr_ycbcr_image = cv2.merge([sr_y_image, hr_cb_image, hr_cr_image])
        sr_image = imgproc.ycbcr2bgr(sr_ycbcr_image)
        new_image_path = image_path.replace('images', 'results')
        cv2.imwrite(new_image_path, sr_image * 255.0)
        return render(request, 'result.html', context={'old_path': ser.data['image'], 'new_path': ser.data['image'].replace('images', 'results')})


class VideoUploadView(View):
    def get(self, request):
        return render(request, 'video.html')

    def post(self, request):
        if request.method == 'POST':
            form = VideoForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save()

        video = str(obj.video)
        print(video)
        cam = cv2.VideoCapture("./media/" + video)
        currentframe = 0
        gap = 10

        while True:
            # reading from frame
            ret, frame = cam.read()

            if ret:
                if currentframe % gap == 0:
                    name = './media/frame/' + str(currentframe) + '.jpg'
                    print('Creating...' + name)
                    cv2.imwrite(name, frame)

                currentframe += 1
            else:
                break
                cam.release()
                cv2.destroyAllWindows()

        return render(request, 'video.html', {
            'uploaded_file_url': obj.video
        })
