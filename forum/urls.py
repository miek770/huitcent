# -*- coding: utf-8 -*-

from django.urls import re_path 
from . import views

urlpatterns = [
    re_path(r'^$', views.index),
    re_path(r'^new/$', views.new_forum),
    re_path(r'^create/$', views.create_forum),
    re_path(r'^edit_preferences/$', views.edit_preferences),
    re_path(r'^do_edit_preferences/$', views.do_edit_preferences),
    re_path(r'^(?P<new_post_id>\d+)/clear_new_post/$', views.clear_new_post),
    re_path(r'^(?P<forum_id>\d+)/$', views.view_forum),
    re_path(r'^(?P<forum_id>\d+)/subscribe/$', views.subscribe_to_forum),
    re_path(r'^(?P<forum_id>\d+)/do_subscribe/$', views.do_subscribe_to_forum),
    re_path(r'^(?P<forum_id>\d+)/new_category/$', views.new_category),
    re_path(r'^(?P<forum_id>\d+)/create_category/$', views.create_category),
    re_path(r'^(?P<forum_id>\d+)/new_topic/$', views.new_topic),
    re_path(r'^(?P<forum_id>\d+)/create_topic/$', views.create_topic),
    re_path(r'^(?P<forum_id>\d+)/search/$', views.search),
    re_path(r'^(?P<forum_id>\d+)/do_search/$', views.do_search),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/$', views.view_topic),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/edit/$', views.edit_topic),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/do_edit/$', views.do_edit_topic),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/do_delete/$', views.do_delete_topic),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/new_thread/$', views.new_thread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/create_thread/$', views.create_thread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/$', views.view_thread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/edit/$', views.edit_thread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/do_edit/$', views.do_edit_thread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/do_delete/$', views.do_delete_thread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/new_post/$', views.new_post),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/create_post/$', views.create_post),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/unread/$', views.unread),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/reply/$', views.reply_post),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/edit/$', views.edit_post),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/do_edit/$', views.do_edit_post),
    re_path(r'^(?P<forum_id>\d+)/(?P<topic_id>\d+)/(?P<thread_id>\d+)/(?P<post_id>\d+)/do_delete/$', views.do_delete_post),
]
