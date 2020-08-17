from django.conf.urls import url, include
from django.contrib import admin
from . import views
urlpatterns = [
    url('view-list/$', views.view_list_event, name='view_list_event'),
    url('participant/$', views.event_participant, name='view_participants_in_event'),
    url('like/$', views.event_like, name='view_likes_in_event'),
    url('comment/$', views.event_comment, name='view_comments_in_event'),
    url('create/$', views.create_event, name='create_event'),
    url('view/$', views.view_event, name='view_event_by_id')
]
