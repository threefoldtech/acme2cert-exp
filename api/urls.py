# -*- coding: utf-8 -*-
""" urls for acme django database """
from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^prefetch$', views.prefetch)
]
