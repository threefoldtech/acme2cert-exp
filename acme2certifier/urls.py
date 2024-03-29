"""acme2certifier URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# pylint: disable=C0330
from django.conf.urls import include, url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.directory, name='index'),
	url(r'^directory$', views.directory, name='directory'),
	url(r'^get_servername$', views.servername_get, name='servername_get'),
	url(r'^trigger$', views.trigger, name='trigger'),
    url(r'^acme/', include('app.urls')),
    url(r'^api/', include('api.urls')),
]
