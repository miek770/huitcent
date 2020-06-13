"""huitcent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from forum import urls as forum_urls
from passwords import urls as passwords_urls
from finance import urls as finance_urls

from huitcent import settings
from django.conf.urls.static import static

# Basé sur http://sjoerdjob.com/post/reusing-django-include-urls-for-index/

urlpatterns = [
    url(r'^forum/', include(forum_urls)),
    url(r'^\Z', include(forum_urls)),
    url(r'^passwords/', include(passwords_urls)),
    url(r'^finance/', include(finance_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^login', auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    url(r'^logout', auth_views.LogoutView.as_view(template_name="registration/logout.html"), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
