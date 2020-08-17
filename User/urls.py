from django.conf.urls import url
from . import views
urlpatterns = [
    url('activity/', views.view_user_activity, name='view_event_by_id')
]
