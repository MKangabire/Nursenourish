# urls.py
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views
from django.views.static import serve
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static
app_name = 'nourse'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile-setup/', views.complete_profile, name='profile_setup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.main, name='home'),
    path('create-post/', views.create_post, name='create_post'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('category/<int:category_id>/', views.category_view, name='posts_by_category'),
    path('search/results/', views.search_view, name='search'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),    
    path('send-message/', views.send_message, name='send_message'),
    path('inbox/<int:recipient_id>/', views.inbox, name='inbox_with_recipient'),
    path('inbox/', views.inbox, name='inbox'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('complete_profile/', views.complete_profile, name='complete'),
    path('search-users/', views.search_users, name='search_users'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        re_path(r'^additional-static/(?P<path>.*)$', serve, {'document_root': settings.ADDITIONAL_STATIC_ROOT}),
    ]