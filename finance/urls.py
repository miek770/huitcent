# -*- coding: utf-8 -*-

from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index),
    re_path(r'^new/$', views.new_group),
    re_path(r'^create/$', views.create_group),
    re_path(r'^(?P<group_id>\d+)/$', views.view_group),
    re_path(r'^(?P<group_id>\d+)/add_member/$', views.add_member),
    re_path(r'^(?P<group_id>\d+)/do_add_member/$', views.do_add_member),
    re_path(r'^(?P<group_id>\d+)/add_transaction/$', views.add_transaction),
    re_path(r'^(?P<group_id>\d+)/(?P<transaction_id>\d+)/delete_transaction/$', views.delete_transaction),
]
