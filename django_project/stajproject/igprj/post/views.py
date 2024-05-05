import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tag, Stream, Follow, Post, Likes
from django.contrib.auth.decorators import login_required
from .forms import NewPostForm, StatusForm
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from userauths.models import Profile
from comment.models import Comment
from comment.forms import CommentForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from userauths.models import Status


# to display the user's stream of posts along with information about users they are following and users who are following them
class IndexView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        posts = Stream.objects.filter(user=user)
        all_users = User.objects.all()
        stories = []

        group_ids = []
        for post in posts:
            group_ids.append(post.post_id)

        post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
        follows = Follow.objects.filter(following=user)
        imfollowing = Follow.objects.filter(follower=user)

        like_count_list = Likes.objects.filter(is_liked=True).values("post_id").annotate(likes=Count("id"))
        like_counts = {l["post_id"]: l["likes"] for l in like_count_list}

        ilike = Likes.objects.filter(user=request.user, is_liked=True).values_list("post_id", flat=True)
        favourite_posts = request.user.profile.favourite.all().values_list("id", flat=True)

        for user in User.objects.all():
            items = []
            for status in user.status.all():
                items.insert(0, {
                    "id": status.id,
                    "type": "",
                    "length": 3,
                    "src": f'/media/{status.file}',
                })
            stories.append({
                "id": str(user.id),
                "photo": f'/media/{user.profile.image}',
                "items": items,
                "name": user.username,
            })

        context = {
            'following': [follow.following for follow in imfollowing],
            'post_items': post_items,
            'followers': [follow.follower for follow in follows],
            'all_users': all_users,
            'like_counts': like_counts,
            'ilike': ilike,
            'favourite_posts': favourite_posts,
            'stories': json.dumps(stories),
        }

        return render(request, 'index.html', context)


class NewPostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = NewPostForm()
        context = {'form': form}
        return render(request, "newpost.html", context)

    def post(self, request, *args, **kwargs):
        user = request.user.id
        tags_objs = []
        # to populate the form with the user's submitted data
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tag')
            tags_list = list(tag_form.split(','))  # house, icecream

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            # to check is a post exists
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user_id=user)
            p.tag.set(tags_objs)
            p.save()
            return redirect('index')
        else:
            form = NewPostForm()

        context = {
            'form': form
        }
        return render(request, "newpost.html", context)


class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        # comment
        comments = Comment.objects.filter(post=post).order_by("-date")
        form = CommentForm()
        context = {
            'form': form,
            'comments': comments,
            'post': post,
            'user': request.user,
            'likes': Likes.objects.filter(post=post).count()
        }
        return render(request, 'post-details.html', context)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST, request.FILES)

        if form.is_valid():
            comment = form.save(commit=False)  # creates a model instance but does not save to the database immediately
            comment.post = post
            comment.user = request.user
            comment.save()
            return HttpResponseRedirect(reverse("post-detail", args=[post_id]))

        context = {
            'form': form,
            'comments': Comment.objects.filter(post=post).order_by("-date"),
            'post': post,
            'user': request.user,
        }
        return render(request, 'post-details.html', context)


class DeleteCommentView(LoginRequiredMixin, View):
    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
        return redirect('post-detail', post_id=comment.post.id)


class LikeView(View):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get("post_id")
        post = Post.objects.get(id=post_id)

        is_liked_by_user = Likes.objects.filter(user=request.user, post=post).exists()

        like_count_list = Likes.objects.filter(is_liked=True).values("post_id").annotate(likes=Count("id"))
        like_counts = {l["post_id"]: l["likes"] for l in like_count_list}
        current_likes = like_counts.get(post_id, 0)

        if is_liked_by_user:
            # unliking
            Likes.objects.filter(user=request.user, post=post).delete()
            like_counts[post_id] = current_likes - 1

        else:
            # liking the post
            Likes.objects.create(user=request.user, post=post, is_liked=True)
            like_counts[post_id] = current_likes + 1

        response = {
            "likes": like_counts[post_id],
            "is_liked_by_user": not is_liked_by_user,
        }

        return HttpResponse(json.dumps(response), content_type="application/json")


class FavouriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        profile = request.user.profile

        if post in profile.favourite.all():
            profile.favourite.remove(post)
            is_favourited = False
        else:
            profile.favourite.add(post)
            is_favourited = True

        response = {
            'is_favourited': is_favourited,
        }

        return JsonResponse(response)


class DeletePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if request.user == post.user:
            post.delete()
            return redirect('profile', username=request.user.username)

        return JsonResponse({"error": "You are not authorized to delete this post."}, status=403)


class AddStoryView(View):
    template_name = 'add_story.html'

    def get(self, request, *args, **kwargs):
        form = StatusForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = StatusForm(request.POST, request.FILES)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            status.save()
            return redirect('index')
        return render(request, self.template_name, {'form': form})


class DeleteStoryView(LoginRequiredMixin, View):
    def get(self, request, story_id):
        story = get_object_or_404(Status, id=story_id, user=request.user)
        if story.user == request.user:
            story.delete()
        return redirect('my-stories')  # Redirect to the my-stories page


class MyStoriesView(LoginRequiredMixin, View):
    template_name = 'my_stories.html'  # Create this template

    def get(self, request, *args, **kwargs):
        user_stories = Status.objects.filter(user=request.user).order_by('-created_at')
        context = {'user_stories': user_stories}
        return render(request, self.template_name, context)