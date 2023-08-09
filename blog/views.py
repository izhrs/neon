from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views import View
from django.views.generic.edit import DeleteView, UpdateView

from blog.forms import PostCreationForm
from blog.models import Category, Post


class IndexView(View):
    def get(self, request):
        featured_post = Post.objects.order_by('-views').first()
        trending_posts = Post.objects.order_by(
            '-views').exclude(id=featured_post.id)[:5]
        random_posts = Post.objects.order_by(
            '?').exclude(id=featured_post.id)[:12]
        categories = Category.objects.order_by('name')

        ctx = {
            'featured_post': featured_post,
            'trending_posts': trending_posts,
            'random_posts': random_posts,
            'categories': categories
        }
        return render(request, 'blog/index.html', ctx)


class PostCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PostCreationForm()
        return render(request, 'blog/form.html', {'form': form})

    def post(slef, request):
        form = PostCreationForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
            messages.success(request, 'Blog post created successfully')
            return redirect('post-detail', post.slug)
        return render(request, 'blog/form.html', {'form': form})


class PostDetailView(View):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        post.views = post.views + 1
        post.save()
        return render(request, 'blog/detail.html', {'post': post})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'excerpt', 'thumbnail', 'category', 'content']
    template_name = 'blog/form.html'

    def test_func(self) -> bool | None:
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        return self.request.user == post.author

    def get_success_url(self):
        messages.success(self.request, 'Blog post updated successfully')
        slug = self.kwargs['slug']
        return reverse_lazy('post-detail', kwargs={'slug': slug})
