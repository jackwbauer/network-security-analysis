from django.urls import path
from . import views

urlpatterns = [
    path('', views.conn_log_list, name='conn_log_list'),
    path('live/', views.conn_log_list_live, name='conn_log_list_live'),
    path('feed/', views.conn_log_feed, name='conn_log_feed')
]