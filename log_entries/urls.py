from django.urls import path
from . import views

urlpatterns = [
    path('', views.conn_log_list, name='conn_log_list'),
]