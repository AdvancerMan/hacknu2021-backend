from django.urls import path, include

urlpatterns = [
    path('', include('memes.urls')),
]

# TODO authentication
