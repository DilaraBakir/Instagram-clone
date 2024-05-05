from django import forms
from comment.models import Comment


class CommentForm(forms.ModelForm):
    # widget to handle the user input and appearance
    body = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Enter a comment'}), required=True)

    # provides meta information
    class Meta:
        model = Comment
        # user will only enter the comment
        fields = ['body']