from django.conf.urls import url, include
from django.contrib import admin
from . import views
urlpatterns = [
    url('list/$', views.view_list_event, name='view_list_event'),
    url('participant/$', views.participate_action, name='participate_action_in_event'),
    url('like/$', views.like_action, name='like_action_in_event'),
    url('comment/$', views.comment_action, name='comment_action_in_event'),
    url('create/$', views.create_event, name='create_event'),
    url('view/$', views.view_event, name='view_event_by_id'),
    url('view/like/$', views.view_list_like, name='view_likes_in_event'),
    url('view/comment/$', views.view_list_comment, name='view_comments_in_event'),
    url('view/participant/$', views.view_list_participant, name='view_participants_in_event'),
]
