from django.urls import path
from . import views


urlpatterns = [

    path('', views.IndexView.as_view(), name="index"),
    path('newpost/', views.NewPostView.as_view(), name="newpost"),
    path('<uuid:post_id>/', views.PostDetailView.as_view(), name="post-detail"),
    # path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('<uuid:post_id>/like', views.LikeView.as_view(), name="like"),
    path('<uuid:post_id>/favourite', views.FavouriteView.as_view(), name="post-favourite"),
    path('comment/<int:comment_id>/delete/', views.DeleteCommentView.as_view(), name='comment-delete'),
    path('post/<uuid:post_id>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('add_story/', views.AddStoryView.as_view(), name='add_story'),
    path('delete_story/<int:story_id>/', views.DeleteStoryView.as_view(), name='delete-story'),
    path('my-stories/', views.MyStoriesView.as_view(), name='my-stories'),

]