from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import random
from django.db.models import SET_NULL


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=50, unique=True)
    picture = models.ImageField(upload_to='static/', default='static/default-profile.png')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Add unique related_name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Add unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_unique_id()
        super(User, self).save(*args, **kwargs)

    @staticmethod
    def generate_unique_id():
        while True:
            unique_id = random.randint(1000, 9999)
            if not User.objects.filter(id=unique_id).exists():
                return unique_id

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='static/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=10, null=True)
    bio = models.TextField(blank=True)
    work_field = models.CharField(max_length=100, blank=True)
    picture = models.ImageField(upload_to='static/', blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Likes(models.Model):
    post = models.ForeignKey(Post, related_name='post_likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'

class Conversation(models.Model):
    participants = models.ManyToManyField(User)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    post = models.ForeignKey(Post, on_delete=SET_NULL, null=True, blank=True)
    message = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Notification for {self.user.username}'



