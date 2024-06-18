from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.http import Http404

from .models import Comments, Post
from .forms import CommentsForm, PostForm


class CommentEditMixin:
    model = Comments
    context_object_name = 'comment'
    form_class = CommentsForm
    pk_url_kwarg = 'comment'
    template_name = 'blog/comment.html'

    def get_queryset(self):
        post = self.kwargs['post']
        comment = self.kwargs['comment']
        queryset = Comments.objects.filter(post_id=post, id=comment)
        if queryset:
            return queryset
        else:
            raise Http404

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.object.post_id}
        )


class PostsListMixin:
    model = Post
    ordering = '-pub_date'
    paginate_by = 10


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})
