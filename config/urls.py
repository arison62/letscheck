"""
URL configuration for enspm_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from .api import api_v1
from apps.core import views as core_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls')),
    path('api/v1/', api_v1.urls),
    path('verify-account/<str:token>/', core_views.verify_account, name='verify_account'),
] + debug_toolbar_urls()
