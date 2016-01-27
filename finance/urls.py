# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.index),
  url(r'^new/$', views.new_group),
  url(r'^create/$', views.create_group),
  url(r'^(?P<group_id>\d+)/$', views.view_group),
  url(r'^(?P<group_id>\d+)/add_member/$', views.add_member),
  url(r'^(?P<group_id>\d+)/do_add_member/$', views.do_add_member),
  url(r'^(?P<group_id>\d+)/add_transaction/$', views.add_transaction),
  url(r'^(?P<group_id>\d+)/(?P<transaction_id>\d+)/delete_transaction/$', views.delete_transaction),
]
