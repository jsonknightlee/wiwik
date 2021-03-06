from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from .models import Post, Comment, Categories
# User Forms
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm, CommentForm, PostForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
import re
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


class IndexView(ListView):
    template_name = 'posts/index.html'
    context_object_name = 'all_posts'

    def get_queryset(self):
        return Post.objects.order_by('-post_date')

    def cats(self, category):
        for instance in Categories.objects.all():
            print(instance)
        context = {"topics": category}
        return render(self, 'posts/index.html', context)


class Details(DetailView):
    model = Post
    template_name = 'posts/detail.html'


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author_comments = request.user
            comment.post = post
            comment.save()
            return redirect('posts:detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'posts/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect(request, 'posts:detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect(request,'posts:detail', pk=post_pk)


def post_create(request):
    if not request.user.is_authenticated():
        return render(request, 'posts/login_user.html')
    else:
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.image = request.FILES['image']
            file_type = post.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'post': post,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'posts/post_form.html', context)
            post.save()
            return render(request, 'posts/detail.html', {'post': post})
        context = {
            "form": form,
        }
    return render(request, 'posts/post_form.html', context)


def welcome(request):
    user = User.objects.filter(user=request.user)
    return render(request, 'posts/welcome.html', {'user': user})


class UserFormView(View):
    form_class = UserForm
    template_name = 'posts/registration_form.html'

    # Create Get and POST logic handling
    # Display Blank Form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # Process form data
    def post(self, request):
        form = self.form_class(request.POST)  # When press submit

        if form.is_valid():

            user = form.save(commit=False)  # Creates object from form

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            subject = 'Thank you for signing up to Wiwik!'
            message = 'We know that your quest for knowledge will lead you on an amazing roads' \
                      ' as you journey with us.\n ' \
                      'Look out for our snippetschool super tips.\n' \
                      'www.wiwik.online to login\n\n' \
                      'Regards,\n\n'\
                      'Wiwik'
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email, settings.EMAIL_HOST_USER]

            send_mail(subject, message, from_email, to_list)

            # returns User objects if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    #  request.user.username
                    return redirect('posts:index')

        return render(request, self.template_name, {'form': form})


def logout_user(request):
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'posts/login_user.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                posts = Post.objects.filter(user=request.user)
                return render(request, 'posts/welcome.html', {'posts': posts})
            else:
                return render(request, 'posts/login_user.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'posts/login_user.html', {'error_message': 'Invalid login'})
    return render(request, 'posts/login_user.html')


def upvote(request, post_id):
    if request.user.is_authenticated():
        p = get_object_or_404(Post, pk=post_id)
        p.upvote += 1
        p.save()
        return render_to_response("posts/upvote.html", {'post_id': post_id, 'type': 'upvote',
                                                        'post': p, 'user': request.user})
    else:
        return HttpResponseRedirect('/login/?next=%s' % request.path)


def down_vote(request, post_id):
    if request.user.is_authenticated():
        p = get_object_or_404(Post, pk=post_id)
        p.upvote -= 1
        p.save()
        return render_to_response("posts/down_vote.html", {'post_id': post_id, 'type': 'down_vote',
                                                        'post': p, 'user': request.user})
    else:
        return HttpResponseRedirect('/login/?next=%s' % request.path)


# Categories
class CategoriesIndex(ListView):
    model = Categories
    context_object_name = 'all_categories'


class CategoriesDetail(DetailView):
    model = Categories
    template_name = 'posts/category_detail.html'


#Search Navigation

def search(request):
    query = request.GET.get("q")
    if query:
        queryset_list = Post.objects.filter(Q(post_title__icontains=query) |
                                        Q(post_body__icontains=query)
                                        ).distinct()
        context = {"queryset_list": queryset_list}
        return render(request, 'posts/search.html', context)
    elif query is None:
        context2 = {"unfound_error": 'Your search returned no values'}
        return render(request, "posts/search.html", context2)
    else:
        context1 = {"error_message": 'Your did not enter anything - Try again'}
        return render(request, "posts/search.html", context1)


def about(request):
    return render(request, 'posts/about.html')
