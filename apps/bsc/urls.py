from django.urls import path

from . import views

app_name = 'bsc'

urlpatterns = [
    path('', views.index, name='index'),
    path('guardar/', views.guardar, name='guardar'),
    path('abrir/', views.abrir, name='abrir'),
    path('cargar/<str:token>/', views.cargar, name='cargar'),
]
