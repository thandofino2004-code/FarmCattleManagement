from django.urls import path
from .import views

app_name = 'cattle'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cattle/', views.cattle_list, name='cattle_list'),
    path('cattle/add/', views.cattle_add, name='cattle_add'),
    path('cattle/<int:cattle_id>/', views.cattle_detail, name='cattle_detail'),
    path('cattle/<int:cattle_id>/edit/', views.cattle_edit, name='cattle_edit'), 
    path('cattle/<int:cattle_id>/delete/', views.cattle_delete, name='cattle_delete'), 
    

]