from .models import Post, Comments
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')
