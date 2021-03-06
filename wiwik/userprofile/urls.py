from django.conf.urls import url
from . import views

app_name = 'userprofile'

urlpatterns = [
            url(r'^profile/(?P<profile_id>\d+)/$', views.user_profile, name='profile'),
            url(r'^update_profile/$', views.update_profile, name='update'),
            url(r'^your_profile/$', views.your_profile, name='your_profile'),
]