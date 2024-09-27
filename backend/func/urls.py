from django.urls import path

from . import views

urlpatterns = [
    path('rozenbrock/', views.rozenbrock),
]
