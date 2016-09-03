from django.conf.urls import include, url
from .feeds import LatestPostsFeed
from . import views

urlpatterns = [
    # url(r'^$', views.PostListView.as_view(), name='post_list'),
    url(r'^$', views.post_list, name='post_list'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'\
    	r'(?P<post>[-\w]+)/$',
    	views.post_detail,
    	name='post_detail'),
    url(r'^(?P<post_id>\d+)/share/$', views.post_share, name='post_share'),
    # Added the following URL pattern to list post by tags.
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list, name='post_list_by_tag'),
    url(r'^feed/$', LatestPostsFeed(), name='post_feed'),
    url(r'^search/$', views.post_search, name='post_search'),
]
