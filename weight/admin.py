from django.contrib import admin
#from .models import Cattle
from .models import WeightRecord
#from health.models import HealthRecord


@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = [
        'cattle',
        'weight_kg',
        'record_date',
    ]
    list_filter = ['record_date']
    search_fields = ['cattle__gov_tag', 'cattle__ear_tag']
    list_editable = ['weight_kg']
    
    fieldsets = (
        ('Animal', {
            'fields': ('cattle',)
        }),
        ('Weight', {
            'fields': ('weight_kg',)
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

# Register your models here.
