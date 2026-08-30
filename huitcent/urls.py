"""huitcent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:    re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:    re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:    re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from forum import urls as forum_urls
from passwords import urls as passwords_urls
from finance import urls as finance_urls

from huitcent import settings
from django.conf.urls.static import static

# Basé sur http://sjoerdjob.com/post/reusing-django-include-urls-for-index/

urlpatterns = [
      re_path(r'^forum/', include(forum_urls)),
      re_path(r'^\Z', include(forum_urls)),
      re_path(r'^passwords/', include(passwords_urls)),
      re_path(r'^finance/', include(finance_urls)),
      re_path(r'^admin/', admin.site.urls),
      re_path(r'^login', auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
      re_path(r'^logout', auth_views.LogoutView.as_view(template_name="registration/logout.html"), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
