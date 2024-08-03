from django import forms
from .models import Post, Comment, Message, Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
            return user

class LoginForm(AuthenticationForm):
    pass

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image', 'content', 'category']

    image = forms.ImageField(required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'content']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomLoginView(LoginView):
    form_class = LoginForm        

class complete_profile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['title', 'work_field', 'bio', 'picture']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['title', 'bio', 'work_field', 'picture']