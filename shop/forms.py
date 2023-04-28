from django import forms
from shop.models import Banners
from django.forms import ModelForm


class BannerForm(ModelForm):
    class Meta:
        model = Banners
        fields = ["image", "product", "alt_text"]


class EditBanner(forms.ModelForm):
    class Meta:
        model = Banners
        fields = ["image", "product", "alt_text"]