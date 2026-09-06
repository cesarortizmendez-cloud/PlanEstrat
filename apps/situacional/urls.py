from django.urls import path

from . import views

app_name = 'situacional'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.solve_api, name='solve_api'),
]
