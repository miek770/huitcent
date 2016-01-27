# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),

    url(r'^new/$', views.new_group),
    url(r'^create/$', views.create_group),
    url(r'^(?P<group_id>\d+)/$', views.group),
    url(r'^(?P<group_id>\d+)/do_delete/$', views.do_delete_group),
    url(r'^(?P<group_id>\d+)/edit/$', views.edit_group),
    url(r'^(?P<group_id>\d+)/save/$', views.save_group),

    url(r'^(?P<group_id>\d+)/create/$', views.create_password),
    url(r'^(?P<group_id>\d+)/new/$', views.new_password),
    url(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/$', views.password),
    url(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/do_delete/$', views.do_delete_password),
    url(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/edit/$', views.edit_password),
    url(r'^(?P<group_id>\d+)/(?P<password_id>\d+)/save/$', views.save_password),
]
