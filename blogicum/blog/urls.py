from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

    path('posts/create/',
         login_required(views.PostCreateView.as_view()),
         name='create_post'),
    path('posts/<int:id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:id>/delete/',
         login_required(views.PostDeleteView.as_view()),
         name='delete_post'),
    path('posts/<int:id>/edit/',
         (views.PostUpdateView.as_view()),
         name='edit_post'),

    path('posts/<int:id>/comment/',
         login_required(views.add_comment),
         name='add_comment'),
    path('posts/<int:post>/edit_comment/<int:comment>/',
         login_required(views.CommentUpdateView.as_view()),
         name='edit_comment'),
    path('posts/<int:post>/delete_comment/<int:comment>/',
         login_required(views.CommentDeleteView.as_view()),
         name='delete_comment'),

    path('profile/<str:username>/',
         views.ProfileListView.as_view(), name='profile'),
    path('profile/edit_profile',
         login_required(views.UserUpdateView.as_view()),
         name='edit_profile'),

    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
]
