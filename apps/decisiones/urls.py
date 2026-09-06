from django.urls import path

from . import views

app_name = 'decisiones'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('unirse/', views.unirse, name='unirse'),
    path('enviar/', views.enviar, name='enviar'),
    path('admin/<str:token>/', views.admin, name='admin'),
    path('cerrar/<str:token>/', views.cerrar, name='cerrar'),
]
