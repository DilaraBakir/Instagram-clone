from django import forms
from .models import Post
from userauths.models import Status


class NewPostForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tag = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Separate tag with comma'}), required=True)

    class Meta:
        model = Post
        # user will enter these
        fields = ['picture', 'caption', 'tag']


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['file']