from django.urls import path

from testapp.views import TestView, GetAllView, AddView

urlpatterns = [
    path('get_hello', TestView.as_view()),
    path('get_all', GetAllView.as_view()),
    path('add', AddView.as_view()),
]
