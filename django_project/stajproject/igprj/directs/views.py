from itertools import chain
from operator import attrgetter
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from directs.models import Message
from django.core.paginator import Paginator
from django.db.models import Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import send_message, get_message
from .utils import Message


class InboxView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        messages = get_message(user=user)
        active_direct = None
        directs = None
        if messages:
            message = messages[0]
            active_direct = message['user'].username
            directs = Message.objects.filter(sender=user, receiver=message['user'])
            directs.update(is_read=True)

            for message in messages:
                if message['user'].username == active_direct:
                    message['unread'] = 0
        context = {
            'directs': directs,
            'active_direct': active_direct,
            'messages': messages,
        }
        return render(request, 'directs/inbox.html', context)


class DirectsView(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = request.user
        messages = get_message(user=user)

        active_direct = username
        directs_me = Message.objects.filter(sender=user, receiver__username=username)
        directs_opposite = Message.objects.filter(sender__username=username, receiver=user)

        directs_opposite.update(is_read=True)
        directs_me.update(is_read=True)
        directs = sorted(
            chain(directs_me, directs_opposite),
            key=attrgetter('date'),
        )

        #directs.update(is_read=True)
        print(user)
        print(username)

        for message in messages:
            if message['user'].username == username:
                message['unread'] = 0

        context = {
            'directs': directs,
            'active_direct': active_direct,
            'messages': messages,
        }
        return render(request, 'directs/directs.html', context)


class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from_user = request.user
        to_user_username = request.POST.get('to_user')
        body = request.POST.get('body')

        to_user = User.objects.get(username=to_user_username)
        send_message(from_user, to_user, body)
        return redirect('inbox')


class UserSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        context = {}
        # if query is not none (not empty)
        if query:
            users = User.objects.filter(Q(username__icontains=query))

            paginator = Paginator(users, 8)
            page_number = request.GET.get('page')
            users_paginator = paginator.get_page(page_number)

            context = {
                'users': users_paginator,
            }
        return render(request, 'directs/search.html', context)


class NewMessageView(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        from_user = request.user
        body = ''
        try:
            to_user = User.objects.get(username=username)
        except Exception as e:
            return redirect('user-search')

        if from_user != to_user:
            send_message(from_user, to_user, body)
        return redirect('inbox')

