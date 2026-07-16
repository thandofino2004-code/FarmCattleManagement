from django.urls import path
from .import views

app_name = 'breeding'

urlpatterns = [
    path('', views.breeding_dashboard, name='breeding_dashboard'),
    path('cattle/<int:cattle_id>/calving/add/', views.calving_record_add, name='calving_record_add'),
    path('pregnancy/<int:pregnancy_id>/edit/', views.pregnancy_record_edit, name='pregnancy_record_edit'),
    path('pregnancy/<int:pregnancy_id>/delete/', views.pregnancy_record_delete, name='pregnancy_record_delete'),
    path('cattle/<int:cattle_id>/pregnancy/add/', views.pregnancy_record_add, name='pregnancy_record_add'),

]