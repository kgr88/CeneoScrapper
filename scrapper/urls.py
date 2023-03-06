from django.urls import path
from . import views


app_name = 'scrapper'
urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('ekstrakcja/', views.ekstrakcja, name='ekstrakcja'),
    path('lista/', views.lista, name='lista'),
    path('autor/', views.autor, name='autor')
]