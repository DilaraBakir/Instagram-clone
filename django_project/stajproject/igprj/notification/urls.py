from django.urls import path
from .views import notifications_view, DeleteNotificationView

urlpatterns = [
    path('', notifications_view, name='notifications'),
    path('notifications/delete-notification/<int:notification_pk>/', DeleteNotificationView.as_view(), name='delete-notification'),
]