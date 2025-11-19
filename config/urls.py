from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('django-admin/', admin.site.urls), 
    path('admin/', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('', include('productos.urls')),
    path('api/gemini/', views.gemini_proxy, name='gemini-proxy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
