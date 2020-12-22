from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

admin.site.site_header = "Адмнистрирование gitbackup"
admin.site.site_title = "Адмнистрирование gitbackup"
admin.site.index_title = "gitbackup"
urlpatterns = [
    path('', RedirectView.as_view(url='admin/', permanent=True)),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
