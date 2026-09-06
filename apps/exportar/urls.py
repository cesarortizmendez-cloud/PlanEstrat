from django.urls import path

from . import views

app_name = 'exportar'

urlpatterns = [
    path('', views.index, name='index'),
    path('xlsx/', views.xlsx, name='xlsx'),
]
