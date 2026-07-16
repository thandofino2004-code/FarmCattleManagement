from django.urls import path
from .import views

app_name = 'health'

urlpatterns = [
    path('', views.health_dashboard, name='health_dashboard'),
    path('cattle/<int:cattle_id>/health/add/', views.health_record_add, name='health_record_add'),
    path('health/<int:record_id>/edit/', views.health_record_edit, name='health_record_edit'),
    path('health/<int:record_id>/delete/', views.health_record_delete, name='health_record_delete'),
    path('vaccination/<int:vax_id>/edit/', views.vaccination_edit, name='vaccination_edit'),
    path('vaccination/<int:vax_id>/delete/', views.vaccination_delete, name='vaccination_delete'),
    path('cattle/<int:cattle_id>/vaccination/add/', views.vaccination_add, name='vaccination_add'),

]