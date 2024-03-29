from django import forms
from django.forms import Textarea

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']
        # fields = ['group', 'text', 'image']


class CommentForm(forms.ModelForm):
    text = forms.CharField(min_length=10)

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'name': Textarea,
        }
