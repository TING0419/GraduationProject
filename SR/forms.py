from django import forms
from .models import UploadVideo


class ImageForm(forms.Form):
    name = forms.TextInput()
    image = forms.ImageField()


class VideoForm(forms.ModelForm):
    class Meta:
        model = UploadVideo
        fields = ['name', 'video']

    def save(self, commit=True):
        video = super().save(commit=False)
        video.file = self.cleaned_data['video']
        if commit:
            video.save()
        return video
