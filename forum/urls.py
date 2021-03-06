# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.index),
  url(r'^new/$', views.new_forum),
  url(r'^create/$', views.create_forum),
  url(r'^edit_preferences/$', views.edit_preferences),
  url(r'^do_edit_preferences/$', views.do_edit_preferences),
  url(r'^(?P<new_post_id>\d+)/clear_new_post/$', views.clear_new_post),
  url(r'^(?P<forum_id>\d+)/$', views.view_forum),
  url(r'^(?P<forum_id>\d+)/subscribe/$', views.subscribe_to_forum),
  url(r'^(?P<forum_id>\d+)/do_subscribe/$', views.do_subscribe_to_forum),
  url(r'^(?P<forum_id>\d+)/new_category/$', views.new_category),
  url(r'^(?P<forum_id>\d+)/create_category/$', views.create_category),
  url(r'^(?P<forum_id>\d+)/new_topic/$', views.new_topic),
  url(r'^(?P<forum_id>\d+)/create_topic/$', views.create_topic),
  url(r'^(?P<forum_id>\d+)/search/$', views.search),
  url(r'^(?P<forum_id>\d+)/do_search/$', views.do_search),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/$', views.view_topic),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/edit/$', views.edit_topic),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/do_edit/$', views.do_edit_topic),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/do_delete/$', views.do_delete_topic),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/new_thread/$', views.new_thread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/create_thread/$', views.create_thread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/$', views.view_thread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/edit/$', views.edit_thread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/do_edit/$', views.do_edit_thread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/do_delete/$', views.do_delete_thread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/new_post/$', views.new_post),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/create_post/$', views.create_post),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/unread/$', views.unread),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/reply/$', views.reply_post),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/edit/$', views.edit_post),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/do_edit/$', views.do_edit_post),
  url(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/do_delete/$', views.do_delete_post),
]
