from django.urls import path
from directs import views


urlpatterns = [

    path('inbox/', views.InboxView.as_view(), name="inbox"),
    path('directs/<username>', views.DirectsView.as_view(), name='directs'),
    path('send/', views.SendMessageView.as_view(), name='send-message'),
    path('new/', views.UserSearchView.as_view(), name='user-search'),
    path('new/<username>', views.NewMessageView.as_view(), name='new-message'),
    path('search/', views.UserSearchView.as_view(), name="search-users"),
    path('', views.InboxView.as_view(), name="message")

]