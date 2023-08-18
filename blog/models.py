from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=64, null=False)
    image = models.ImageField(
        upload_to='blog/categories/', default='blog/categories/default.webp')

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=False, max_length=255, unique=True)
    excerpt = models.CharField(
        max_length=255, null=False)
    thumbnail = models.ImageField(
        upload_to='blog/thumbnails/', default='blog/thumbnails/default')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    content = RichTextUploadingField()

    views = models.IntegerField(default=1)
    likes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
