from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('escalas/', include('escalas.urls')),  # Inclui as URLs do app escalas com o prefixo /escalas/
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)