from django.shortcuts import get_object_or_404, redirect
from blog.models import Post, Category
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentsForm, UserForm
from .models import Comments
from django.db.models import Count
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  DetailView)
from django.urls import reverse
from django.utils import timezone
from django.http import Http404


User = get_user_model()


class CommentEditMixin():
    model = Comments
    context_object_name = 'comment'
    form_class = CommentsForm
    pk_url_kwarg = 'comment'
    pk_filed = 'id'
    template_name = 'blog/comment.html'

    def get_queryset(self):
        post = self.kwargs['post']
        comment = self.kwargs['comment']
        queryset = Comments.objects.filter(post_id=post, id=comment)
        return queryset

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.object.post_id}
        )


class ListMixin():
    model = Post
    ordering = '-pub_date'
    paginate_by = 10


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin():
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class PostCreateView(PostMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):
    pk_url_kwarg = 'id'

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs.get(self.pk_url_kwarg))

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.id])


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):
    pk_url_kwarg = 'id'


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.author == self.request.user:
            post = get_object_or_404(Post, id=self.object.id)
        else:
            post = get_object_or_404(Post,
                                     is_published=True,
                                     id=self.object.id)
        context['post'] = post
        context['form'] = CommentsForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostListView(ListMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return super().get_queryset().filter(category__is_published=True,
                                             is_published=True,
                                             pub_date__lte=timezone.now()
                                             ).annotate(
                                                 comment_count=Count(
                                                     "comments"))


def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentsForm(request.POST)

    if User.is_authenticated:
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
        return redirect('blog:post_detail', id=id)


class CommentUpdateView(OnlyAuthorMixin, CommentEditMixin, UpdateView):
    pass


class CommentDeleteView(OnlyAuthorMixin, CommentEditMixin, DeleteView):
    pass


class ProfileListView(ListMixin, ListView):
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User,
                                               username=self.kwargs['username']
                                               )
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            author__username=self.kwargs['username']).annotate(
                comment_count=Count("comments"))
        if get_object_or_404(User,
                             username=self.kwargs['username']
                             ) == self.request.user:
            queryset = queryset.filter(author=self.request.user)
        else:
            queryset = queryset.filter(pub_date__lte=timezone.now())
        return queryset


class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class CategoryListView(ListMixin, ListView):
    template_name = 'blog/category.html'
    pk_url_kwarg = 'category_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'])
        if not category.is_published:
            raise Http404
        context['category'] = category
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            category__is_published=True,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__slug=self.kwargs['category_slug']).annotate(
                comment_count=Count("comments"))
