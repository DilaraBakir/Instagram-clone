import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.urls import resolve
from post.models import Post, Follow, Stream, Likes
from .models import Profile
from django.db import transaction
from userauths.forms import EditProfileForm, UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin



class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)
        url_name = resolve(request.path).url_name  # to get the current url's view name

        if url_name == 'profile':
            posts = Post.objects.filter(user=user).order_by('-posted')
        else:
            posts = profile.favourite.all()

        post_count = Post.objects.filter(user=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(following=user).count()

        # follow status
        follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

        # pagination
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        posts_paginator = paginator.get_page(page_number)
        context = {
            'posts_paginator': posts_paginator,
            'profile': profile,
            'posts': posts,
            'url_name': url_name,
            'post_count': post_count,
            'followers_count': followers_count,
            'following_count': following_count,
            'follow_status': follow_status,

        }
        return render(request, 'profile.html', context)


class FollowView(LoginRequiredMixin, View):
    def get(self, request, username, option):
        user = request.user
        following = get_object_or_404(User, username=username)
        try:
            # follow status
            f, created = Follow.objects.get_or_create(follower=user, following=following)
            # unfollowing
            if int(option) == 0:
                f.delete()
                Stream.objects.filter(following=following, user=user).all().delete()
            else:
                # if follow we retrieve the last ten posts the user posted
                posts = Post.objects.filter(user=following)[:10]
                #  to ensure data consistency, adding posts to stream ensuring that all are added or , if success all saved if not changes are undone
                with transaction.atomic():
                    for post in posts:
                        stream = Stream(post=post, user=user, date=post.posted, following=following)
                        stream.save()
            return HttpResponseRedirect(reverse('profile', args=[username]))

        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('profile', args=[username]))


class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):   # to retrieve data and render a template
        user = request.user.id
        profile = Profile.objects.get(user__id=user)
        form = EditProfileForm(instance=profile)
        context = {
            'form': form,
        }
        return render(request, 'edit-profile.html', context)

    def post(self, request):   # creating or updating the resources
        user = request.user.id
        profile = Profile.objects.get(user__id=user)
        form = EditProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            new_image = form.cleaned_data.get('picture')
            if new_image:
                profile.image.delete()  # Delete the old image if a new one is provided
                profile.image = new_image

            # profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.bio = form.cleaned_data.get('bio')
            profile.url = form.cleaned_data.get('url')
            profile.save()
            return redirect('profile', profile.user.username)
        else:
            print(form.errors)


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            user_form = UserRegisterForm()
            profile_form = EditProfileForm()
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
            }
            return render(request, 'sign-up.html', context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            user_form = UserRegisterForm(request.POST)
            if user_form.is_valid():
                user_form.save()

                username = user_form.cleaned_data['username']
                password = user_form.cleaned_data['password1']

                new_user = authenticate(username=username, password=password)
                login(request, new_user)

                return redirect(reverse('editprofile'))

            context = {
                'user_form': user_form,
            }
            return render(request, 'sign-up.html', context)
