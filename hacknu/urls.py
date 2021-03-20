from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', include('testapp.urls')),
    path('api/v1/', include('hacknu.api_v1_urls')),
]
