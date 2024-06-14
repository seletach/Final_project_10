from .models import Post, Comments
from django.contrib.auth import get_user_model
from django import forms
from django.core.mail import send_mail


User = get_user_model()


class PostForm(forms.ModelForm):

    def clean(self):
        super().clean()
        title = self.cleaned_data['title']
        category = self.cleaned_data['category']
        if title:
            send_mail(
                subject=f'Новый пост {title} в категории {category}',
                message=f'{title} {category}',
                from_email='post_form@acme.not',
                recipient_list=['admin@blogicum.not'],
                fail_silently=True,
            )

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
