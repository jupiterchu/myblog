"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin

from django.urls import path, include

from djangoProject import settings
from myblog.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view()),
    path('<int:year>/', DetailView.as_view()),
    path('<str:year>/', DetailView.as_view()),
    path('archives/', ArchiveView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('categories/<str:name>/', CategoryView.as_view()),
    path('tags/', TagView.as_view()),
    path('tags/<str:name>/', TagView.as_view()),
    path(r'mdeditor/', include('mdeditor.urls')),
]+ static(settings.STATIC_URL) + static(settings.MEDIA_URL)
