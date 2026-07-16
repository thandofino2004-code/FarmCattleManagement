from django.contrib import admin
from cattle.models import Cattle
from .models import HealthRecord
from .models import Vaccine
from .models import Vaccination

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = [
        'cattle',
        'record_date',
        'health_status',
        'symptoms',

    ]
    list_filter = ['health_status', 'record_date']
    search_fields = ['cattle_gov_tag', 'cattle_ear_tag', 'symptoms']
    list_editable = ['health_status']

    fieldsets = (
        ('Animal', {
            'fields':('cattle',)
        }),
        ('Health Information', {
            'fields': ('health_status', 'symptoms', 'treatment', 'notes')
        })
    )

@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'default_interval_days']
    search_fields = ['name', 'manufacturer']

@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display=[
        'cattle',
        'vaccine',
        'date_administered',
        'next_due_date',
        'is_due'
    ]
    list_filter = ['vaccine', 'date_administered']
    search_fields = ['cattle__gov_tag', 'cattle__ear_tag', 'vaccine__name']
    list_editable = ['date_administered', 'next_due_date']

    fieldsets = (
         ('Animal', {
            'fields': ('cattle',)
        }),
        ('Vaccine Details', {
            'fields': ('vaccine', 'batch_number', 'dosage', 'veterinarian')
        }),
        ('Dates', {
            'fields': ('date_administered', 'next_due_date')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        )
    
    def is_due(self, obj):
        """Show if vaccination is due"""
        if obj.next_due_date:
            from datetime import date
            return obj.next_due_date <= date.today()
        return False
    is_due.boolean = True
    is_due.short_description = "Due?"


# Register your models here.
