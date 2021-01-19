from django import forms
from .models import Subject, Images


class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ('title', 'level', 'content')


class ImageForm(forms.ModelForm):

    class Meta:
        model = Images
        fields = ('image', )


ImageFormSet = forms.models.inlineformset_factory(Subject, Images, form=ImageForm, extra=1)
