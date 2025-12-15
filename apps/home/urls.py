from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('faq', views.faq_page, name='faq'),
    path('verify', views.verify_page, name='verify'),
    path('index/', views.home_page, name='index'),
]
