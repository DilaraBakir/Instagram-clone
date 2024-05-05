from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from notification.models import Notification
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return obj.sender.username if obj.sender else None

    class Meta:
        model = Notification
        fields = ['action', 'post', 'comment', 'sender', 'date']


class NotificationView(LoginRequiredMixin, APIView):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-date')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


def notifications_view(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-date')
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification.html', context)


class DeleteNotificationView(View):
    def post(self, request, notification_pk):
        notification = get_object_or_404(Notification, pk=notification_pk)
        # Make sure the notification belongs to the current user (optional)
        if notification.receiver == request.user:
            notification.delete()
        return redirect('notifications_view')  # Replace 'notifications' with your actual notifications view name