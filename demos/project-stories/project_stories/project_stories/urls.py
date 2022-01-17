"""project_stories URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import os

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from project_stories import views


PRODUCTION = bool(os.getenv("PRODUCTION", False))


urlpatterns = [
    path('', views.home, name="homepage"),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('user/', include('users.urls')),
    path('stories/', include('stories.urls')),
    path('comments/', include('django_comments_xtd.urls')),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if not PRODUCTION:
    urlpatterns += [path('rosetta/', include('rosetta.urls'))]
