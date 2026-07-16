from django.urls import path
from .import views

app_name = 'weight'

urlpatterns = [
    path('', views.weight_dashboard, name='weight_dashboard'),
    path('weight/add/', views.weight_record_add, name='weight_record_add'),
   # path('cattle/<int:cattle_id>/add/', views.weight_record_add, name='weight_record_add_cattle'),  
    path('weight/<int:weight_id>/edit/', views.weight_record_edit, name='weight_record_edit'),
    path('weight/<int:weight_id>/delete/', views.weight_record_delete, name='weight_record_delete'),
]