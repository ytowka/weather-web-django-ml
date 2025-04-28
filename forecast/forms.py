from django import forms
from .models import WeatherDataset

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = WeatherDataset
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.csv'})
        }