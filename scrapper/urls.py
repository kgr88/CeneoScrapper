from django.urls import path
from . import views


app_name = 'scrapper'
urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('ekstrakcja/', views.ekstrakcja, name='ekstrakcja'),
    path('lista/', views.lista, name='lista'),
    path('autor/', views.autor, name='autor'),
    path('produkt/', views.produkt, name='produkt'),
    path('produkt/download/<int:product_id>', views.download_opinions, name='download_opinions'),
    path('produkt/wykresy/<int:product_id>', views.show_graphs, name='show_graphs'),
]