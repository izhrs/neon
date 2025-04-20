from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import slugify
from django.views import View
from verify_email.email_handler import ActivationMailManager

from blog.models import Post
from users.forms import UserProfileForm, UserRegisterForm
from users.models import Profile


class RegisterView(View):
    def get(self, request):

        try:
            user = User.objects.get(username=request.user.username)
            if user:
                return redirect('index')
        except:
            form = UserRegisterForm()
            return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            ActivationMailManager.send_verification_link(request, form)
            messages.success(
                request, 'Account created! Please verify your email before login')
            return redirect('login')
        else:
            return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        url = self.get_redirect_url()
        print(url)
        return url or reverse('user-profile', kwargs={'username': self.request.user.username})


class CheckUsernameExists(View):
    def post(self, request):
        username = request.POST.get('username')

        if not len(username) > 2:
            return HttpResponse('<small class="text-error pl-1">Username too short</small>')
        elif not slugify(username) == username:
            return HttpResponse('<small class="text-error pl-1">Invalid username, special characters will be removed if submitted</small>')
        else:
            user = User.objects.filter(username=username).exists()
            if user:
                return HttpResponse('<small class="text-error pl-1">Username already taken</small>')

            else:
                return HttpResponse('<small class="text-success pl-1">Username available</small>')


class ProfileView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        user_is_owner = False
        if user == request.user:
            user_is_owner = True
        profile = get_object_or_404(Profile, user=user)
        posts_count = Post.objects.filter(author=user).count()

        ctx = {
            'user_is_owner': user_is_owner,
            'profile': profile,
            'posts_count': posts_count,
        }
        return render(request, 'users/profile.html', ctx)


class ProfileRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect('user-profile', request.user.username)


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return profile.user.id == self.request.user.id

    def get(self, request, username):
        profile = get_object_or_404(Profile, user=request.user)
        if not profile.user.username == username:
            return redirect('user-profile-update', profile.user.username)
        form = UserProfileForm(instance=profile)
        return render(request, 'users/profile_update.html', {'form': form, 'profile': profile})

    def post(self, request, username):
        profile = get_object_or_404(Profile, user=request.user)
        user = request.user
        uname = request.POST.get('username')
        if len(uname) > 2:
            try:
                user.username = slugify(uname)
                user.save()
                username = uname
            except:
                messages.error(request, 'username not changed, already taken')
        else:
            messages.warning(
                request, f'username not changed, {uname} is too short')
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{username}'s profile updated successfully")
            return redirect('user-profile', username)
        messages.error(request, 'there were errors in the form')
        return render(request, 'users/profile_update.html', {'form': form, 'profile': profile})


class SubscribeView(LoginRequiredMixin, View):
    def get(self, request):
        email = request.user.email
        template = render_to_string(
            'partials/email.html', {'username': request.user.username})
        profile = get_object_or_404(Profile, user=request.user)
        if not profile.subscribed:
            profile.subscribed = True
            profile.save()
            send_mail(
                'Thank you for subscribing to Poeticcode',
                template,
                settings.EMAIL_HOST_USER,
                [email],
            )

        return redirect('index')
