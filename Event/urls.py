from django.conf.urls import url, include
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^list/$', views.view_list_event, name='view_list_event'),
    url(r'^participant/$', views.participate_action, name='participate_action_in_event'),
    url(r'^like/$', views.like_action, name='like_action_in_event'),
    url(r'^comment/$', views.comment_action, name='comment_action_in_event'),
    url(r'^create/$', views.create_event, name='create_event'),
    url(r'^view/$', views.view_event, name='view_event_by_id'),
    url(r'^view/like/$', views.view_list_like, name='view_likes_in_event'),
    url(r'^view/comment/$', views.view_list_comment, name='view_comments_in_event'),
    url(r'^view/participant/$', views.view_list_participant, name='view_participants_in_event'),
]
