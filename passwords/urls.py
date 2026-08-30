# -*- coding: utf-8 -*-

from django.urls import re_path
from . import views

urlpatterns = [
      re_path(r'^$', views.index),

      re_path(r'^new/$', views.new_group),
      re_path(r'^create/$', views.create_group),
      re_path(r'^(?P<group_id>\d+)/$', views.group),
      re_path(r'^(?P<group_id>\d+)/do_delete/$', views.do_delete_group),
      re_path(r'^(?P<group_id>\d+)/edit/$', views.edit_group),
      re_path(r'^(?P<group_id>\d+)/save/$', views.save_group),

      re_path(r'^(?P<group_id>\d+)/create/$', views.create_password),
      re_path(r'^(?P<group_id>\d+)/new/$', views.new_password),
      re_path(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/$', views.password),
      re_path(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/do_delete/$', views.do_delete_password),
      re_path(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/edit/$', views.edit_password),
      re_path(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/save/$', views.save_password),
]
