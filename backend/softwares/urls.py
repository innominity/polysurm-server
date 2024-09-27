from django.urls import path
from . import views

urlpatterns = [
   path('', views.software_list),
   path('<slug:app_name>/', views.app_main),
   path('<slug:app_name>/info/', views.app_info),
   path('<slug:app_name>/params/', views.app_params),
]
